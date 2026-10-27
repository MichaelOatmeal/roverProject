import time
import queue
import struct

import serial
import serial.tools.list_ports

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Vector3, TransformStamped, Twist
from std_msgs.msg import Float32
from sensor_msgs.msg import Imu, MagneticField, Temperature
from nav_msgs.msg import Odometry

from rover_interfaces.msg import MotorCommand
from rover_interfaces.msg import MotorRPM


class ArduinoNode(Node):

  def __init__(self):
    super().__init__("arduino_node")
    self.frame = 'imu_link'
    self.radius = 0.05    # wheel radius
    self.width = 0.23    # track width
    self.max_rpm = 251.0    # max rpm
    self.odom_frame = 'odom'
    self.base_frame = 'base_link'
    self.last = self.get_clock().now()

    self.sx = 0.0
    self.sx_1 = 0.0


    self.get_logger().info("Starting Arduino node")


    # serial configuration    -----------------------

    self.baudrate = 230400

    self.serial_port = self.find_arduino()


    # Packet state    -------------------------------

    # global bidirectional rolling packet number
    self.packet_sequence = 0

    # queue for outgoing serial data
    self.serial_queue = queue.Queue()

    # buffer for incoming serial data
    self.rx_buffer = bytearray()


    # ROS publishers    ------------------------------

    ''' don't publish raw data
    self.motor_rpm_publisher = self.create_publisher(
      MotorRPM,					# custom MotorRPM format
      "/motor_rpm",			# topic name
      10								# message backlog size
    )

    self.accel_raw_publisher = self.create_publisher(
      Vector3,
      "/raw/accel",			# topic name
      10								# message backlog size
    )

    self.gyro_raw_publisher = self.create_publisher(
      Vector3,
      "/raw/gyro",			# topic name
      10								# message backlog size
    )

    self.mag_raw_publisher = self.create_publisher(
      Vector3,
      "/raw/mag",				# topic name
      10								# message backlog size
    )

    self.temperature_raw_publisher = self.create_publisher(
      Float32,
      "/raw/temperature",   # topic name
      10								# message backlog size
    )
    '''

    self.imu_publisher = self.create_publisher(
      Imu,
      "/imu",		        # topic name
      10								# message backlog size
    )

    self.mag_publisher = self.create_publisher(
      MagneticField,
      "/mag",		        # topic name
      10								# message backlog size
    )
  
    self.temperature_publisher = self.create_publisher(
      Temperature,
      "/temperature",		# topic name
      10								# message backlog size
    )

    self.odom_pub = self.create_publisher(
      Odometry, 
      '/odom', 
      10
    )


    # ROS subscribers    ------------------------------

    self.motor_subscription = self.create_subscription(
      MotorCommand,
      "/cmd_motors",
      self.motor_command_callback,		# function to run when when topic updated
      10
    )


    # timers (clocks)    ------------------------------

    self.serial_timer = self.create_timer(
      0.001,									# 1000Hz clock
      self.serial_update			# function to run every tick
    )

    self.heartbeat_timer = self.create_timer(
      0.5,										# 2Hz clock
      self.heartbeat					# function to run every tick
    )

    self.get_logger().info("Arduino node started")



  # serial discovery    ================================

  def find_arduino(self):

    while rclpy.ok():		# if running

      ports = serial.tools.list_ports.comports()

      for port in ports:

        self.get_logger().debug(
          f"Found serial device: "
          f"{port.device} ({port.description})")

        if (
          "arduino" in port.description.lower()
          or port.device.startswith("/dev/ttyUSB")
          or port.device.startswith("/dev/ttyACM")):

          try:
            connection = serial.Serial(
              port=port.device,
              baudrate=self.baudrate,
              timeout=0.1,							# wait 100ms before moving on
              write_timeout=0.1)				# wait 100ms before moving on

            self.get_logger().info(f"Connected to {port.device}")

            time.sleep(2)		# in case Arduino resets on connection

            # clear garbage serial IO 
            connection.reset_input_buffer()
            connection.reset_output_buffer()

            return connection

          except serial.SerialException as error:
            self.get_logger().warning(f"Could not open {port.device}: {error}")

      self.get_logger().warning("No Arduino found. Retrying in 2 seconds...")

      time.sleep(2)


  # CRC    ============================================

  @staticmethod
  def crc8(data):

    crc = 0x00

    for byte in data:

      crc ^= byte

      for _ in range(8):

        if crc & 0x80:
          crc = ((crc << 1) ^ 0x07) & 0xFF
        else:
          crc = (crc << 1) & 0xFF

    return crc


  # CRC validation    =================================

  def validate_packet_crc(self, packet):

    if len(packet) != 19:
      return False

    received_crc = packet[18]

    calculated_crc = self.crc8(packet[:18])

    return received_crc == calculated_crc


  # motor packet    ===================================

  def make_motor_packet(self, motor0, motor1):

    sequence = self.packet_sequence

    self.packet_sequence = (self.packet_sequence + 1) & 0xFF

    data = struct.pack(
      "<hh",
      motor0,
      motor1)
    
    packet = (
      b"\x10"
      + bytes([sequence])
      + data
      + b"\x00" * 12)

    crc = self.crc8(packet)

    return packet + bytes([crc])


  # heartbeat packet    ===============================

  def make_heartbeat_packet(self):

    sequence = self.packet_sequence

    self.packet_sequence = (self.packet_sequence + 1) & 0xFF

    packet = (
      b"\xFE"
      + bytes([sequence])
      + b"\x00" * 16)

    crc = self.crc8(packet)
    return packet + bytes([crc])


  # ROS /cmd_motors callback    ======================

  def motor_command_callback(self, msg):

    self.get_logger().debug(
      f"Motor command: "
      f"M0={msg.motor0}, M1={msg.motor1}")

    packet = self.make_motor_packet(
      msg.motor0,
      msg.motor1)

    self.get_logger().info(packet.hex())

    self.serial_queue.put_nowait(packet)


  # Serial update    =================================

  def serial_update(self):

    # read incoming serial data    -------------------

    try:

      bytes_available = self.serial_port.in_waiting

      if bytes_available > 0:
        data = self.serial_port.read(bytes_available)

        self.rx_buffer.extend(data)

    except serial.SerialException as error:
      self.get_logger().warning(f"Serial read error: {error}")
      return


    # parse packets    -------------------------------

    while True:

      packet = self.incoming_read()

      if packet is None:
        break

      self.incoming_parse(packet)

    # send one queued packet    ----------------------

    try:
      packet = self.serial_queue.get_nowait()

    except queue.Empty:
      return

    frame = (
      b"\xAA"
      + packet
      + b"\x55")

    try:
      self.serial_port.write(frame)
      self.get_logger().debug(packet)


    except serial.SerialTimeoutException as error:
      self.get_logger().warning(f"Serial write timeout: {error}")

    except serial.SerialException as error:
      self.get_logger().warning(f"Serial write error: {error}")


  # incoming packet extraction    =====================

  def incoming_read(self):
    # find start delimiter
    try:
      start_index = self.rx_buffer.index(0xAA)

    except ValueError:
      # no start delimiter in the buffer
      self.rx_buffer.clear()
      return None

    # discard garbage before AA
    if start_index > 0:
      del self.rx_buffer[:start_index]

    # wait for complete frame
    if len(self.rx_buffer) < 21:
      return None

    # check end delimiter
    if self.rx_buffer[20] != 0x55:
      # invalid frame, drop the current AA and search for the next
      del self.rx_buffer[0]
      return None

    packet = bytes(self.rx_buffer[1:20])    # extract 19-byte packet

    del self.rx_buffer[:21]    # Remove complete frame from buffer

    return packet


  # incoming packet parser    ========================

  def incoming_parse(self, packet):
    global motor_rpm_msg, accel_msg, gyro_msg, mag_msg, temp_msg

    if len(packet) != 19:
      return


    if not self.validate_packet_crc(packet):
      self.get_logger().warning("Received packet with invalid CRC")
      return

    packet_id = packet[0]


    # MOT_OUT    --------------------------------------
    
    if packet_id == 0x11:

      motor0, motor1 = struct.unpack(
        "<hh",
        packet[2:6])

      motor_rpm_msg = MotorRPM()
      motor_rpm_msg.motor0 = float(motor0)
      motor_rpm_msg.motor1 = float(motor1)
      #motor_rpm_msg.motor2 = float(motor2)
      #motor_rpm_msg.motor3 = float(motor3)

      #self.motor_rpm_publisher.publish(msg)


    # ACCEL    ----------------------------------------
    
    elif packet_id == 0x20:

      x, y, z = struct.unpack(
        "<fff",
        packet[2:14])

      accel_msg = Vector3()

      accel_msg.x = x
      accel_msg.y = y
      accel_msg.z = z

      #self.accel_raw_publisher.publish(accel_msg)

   
    # MAG    -------------------------------------------

    elif packet_id == 0x21:

      x, y, z = struct.unpack(
        "<fff",
        packet[2:14])

      mag_msg = Vector3()

      mag_msg.x = x
      mag_msg.y = y
      mag_msg.z = z

      #self.mag_raw_publisher.publish(mag_msg)


    # GYRO    -----------------------------------------

    elif packet_id == 0x22:

      x, y, z = struct.unpack(
        "<fff",
        packet[2:14])

      gyro_msg = Vector3()

      gyro_msg.x = x
      gyro_msg.y = y
      gyro_msg.z = z

      #self.gyro_raw_publisher.publish(gyro_msg)

      self.ros_bridge()    # update all values on gyro update (gyro is most often)


    # TEMP    -----------------------------------------

    elif packet_id == 0x31:

      temperature = struct.unpack(
        "<3sf",
        packet[2:9])[1]

      temp_msg = Float32()

      temp_msg.data = temperature

      #self.temperature_raw_publisher.publish(temp_msg)


    # HEARTBEAT    ------------------------------------

    elif packet_id == 0xFE:
      
      self.get_logger().debug("Received heartbeat")


    # EMERGENCY    ------------------------------------

    elif packet_id == 0x01:
      
      self.get_logger().warning("Received EMG packet")


    # ERROR    ----------------------------------------

    elif packet_id == 0x02:

      self.get_logger().warning("Received ERR packet")


    # Unknown packet    -------------------------------

    else:

      self.get_logger().debug(f"Unknown packet ID: 0x{packet_id:02X}")


  # convert to conventional ros msg    ===============

  def ros_bridge(self):
    global motor_rpm_msg, accel_msg, gyro_msg, mag_msg, temp_msg

    msg = Imu()
    msg.header.frame_id = self.frame
    msg.header.stamp = self.get_clock().now().to_msg()
    msg.linear_acceleration = accel_msg
    msg.angular_velocity = gyro_msg
    self.imu_publisher.publish(msg)

    msg1 = MagneticField()
    msg1.header.frame_id = self.frame
    msg1.header.stamp = self.get_clock().now().to_msg()
    msg1.magnetic_field = mag_msg
    self.mag_publisher.publish(msg1)

    msg2 = Temperature()
    msg2.header.frame_id = self.frame
    msg2.header.stamp = self.get_clock().now().to_msg()
    msg2.temperature = temp_msg
    self.temperature_publisher.publish(msg2)

    self.rpm_to_odom()

    msg3 = Odometry()
    msg3.header.frame_id = 'odom'
    msg3.child_frame_id = 'base_link'
    msg3.header.stamp = self.get_clock().now().to_msg()
    msg3.pose.pose.position.x = self.x
    msg3.pose.pose.position.y = self.y
    msg3.pose.pose.orientation.z = self.qz
    msg3.pose.pose.orientation.w = self.qw
    msg3.twist.twist.linear.x = self.v
    msg3.twist.twist.angular.z = self.w
    msg3.twist.covariance[0]  = 0.01   # vx variance
    msg3.twist.covariance[35] = 0.05   # vyaw variance, bigger so less trust than IMU

  def rpm_to_odom(self):
    now = self.get_clock().now()
    if self.last is None:
      self.last = now
      return
    dt = (now - self.last).nanoseconds * 1e-9
    self.last = now
    if dt <= 0.0 or dt > 1.0:    # skip bad or stale intervals
      return

    k = 2.0 * math.pi / 60.0 * self.radius    # RPM -> m/s
    vl = k * (motor_rpm_msg.motor0 + motor_rpm_msg.motor3) / 2
    vr = k * (motor_rpm_msg.motor1 + motor_rpm_msg.motor2) / 2

    self.v = (vr + vl) / 2.0    # forward speed
    self.w = (vr - vl) / self.width    # yaw rate

    # midpoint integration
    th_mid = self.th + self.w * dt / 2.0
    self.x += self.v * math.cos(th_mid) * dt    # x displacement
    self.y += self.v * math.sin(th_mid) * dt    # y displacement
    self.th += self.w * dt

    self.qz, self.qw = math.sin(self.th / 2.0), math.cos(self.th / 2.0)
    self.stamp = now.to_msg()


  # =====================================================
  # Heartbeat
  # =====================================================

  def heartbeat(self):

    packet = self.make_heartbeat_packet()

    frame = (
      b"\xAA"
      + packet
      + b"\x55")

    try:
      self.serial_port.write(frame)

    except serial.SerialTimeoutException as error:
      self.get_logger().warning(f"Serial write timeout: {error}")

    except serial.SerialException as error:
      self.get_logger().warning(f"Serial write error: {error}")


  # =====================================================
  # Shutdown
  # =====================================================

  def close(self):

    if self.serial_port is not None:

      try:
        self.serial_port.close()

      except serial.SerialException:
        pass


# =========================================================
# Main
# =========================================================

def main():

  rclpy.init()

  node = ArduinoNode()

  try:
    rclpy.spin(node)

  except KeyboardInterrupt:
    pass

  finally:
    node.close()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
  main()
