import time
import queue
import struct

import serial
import serial.tools.list_ports

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Vector3
from std_msgs.msg import Float32

from rover_interfaces.msg import MotorCommand
from rover_interfaces.msg import MotorRPM


class ArduinoNode(Node):

  def __init__(self):
    super().__init__("arduino_node")

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

    self.motor_rpm_publisher = self.create_publisher(
      MotorRPM,					# custom MotorRPM format
      "/motor_rpm",			# topic name
      10								# message backlog size
    )

    self.accel_publisher = self.create_publisher(
      Vector3,
      "/imu/accel",			# topic name
      10								# message backlog size
    )

    self.gyro_publisher = self.create_publisher(
      Vector3,
      "/imu/gyro",			# topic name
      10								# message backlog size
    )

    self.mag_publisher = self.create_publisher(
      Vector3,
      "/imu/mag",				# topic name
      10								# message backlog size
    )

    self.temperature_publisher = self.create_publisher(
      Float32,
      "/temperature",		# topic name
      10								# message backlog size
    )


    # ROS subscribers    ------------------------------

    self.motor_subscription = self.create_subscription(
      MotorCommand,
      "/cmd_motors",
      self.motor_command_callback,		# function to run when when topic updated
      10
    )
    self.motor_subscription


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

      msg = MotorRPM()

      msg.motor0 = motor0
      msg.motor1 = motor1

      self.motor_rpm_publisher.publish(msg)


    # ACCEL    ----------------------------------------
    
    elif packet_id == 0x20:

      x, y, z = struct.unpack(
        "<fff",
        packet[2:14])

      msg = Vector3()

      msg.x = x
      msg.y = y
      msg.z = z

      self.accel_publisher.publish(msg)

   
    # MAG    -------------------------------------------

    elif packet_id == 0x21:

      x, y, z = struct.unpack(
        "<fff",
        packet[2:14])

      msg = Vector3()

      msg.x = x
      msg.y = y
      msg.z = z

      self.mag_publisher.publish(msg)


    # GYRO    -----------------------------------------

    elif packet_id == 0x22:

      x, y, z = struct.unpack(
        "<fff",
        packet[2:14])

      msg = Vector3()

      msg.x = x
      msg.y = y
      msg.z = z

      self.gyro_publisher.publish(msg)


    # TEMP    -----------------------------------------

    elif packet_id == 0x31:

      temperature = struct.unpack(
        "<3sf",
        packet[2:9])[1]

      msg = Float32()

      msg.data = temperature

      self.temperature_publisher.publish(msg)


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
