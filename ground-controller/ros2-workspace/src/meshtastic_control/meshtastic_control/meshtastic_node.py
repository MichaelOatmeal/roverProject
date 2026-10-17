import rclpy
from rclpy.node import Node

import time

from std_msgs.msg import String
from std_msgs.msg import Float32
from rover_interfaces.msg import GlobalPosition
from rover_interfaces.msg import MeshtasticPacket


from serial.tools import list_ports

import meshtastic
import meshtastic.serial_interface

from pubsub import pub


class MeshtasticNode(Node):

  TARGET_SER = "E072A1D77B48"    # SER ID of meshtastic device over USB (via 'lsusb' command)


  def __init__(self):
    super().__init__('meshtastic_node')    # begin node


    # python pubsub subscribers --------------------------------

    pub.subscribe(self.local_node_connected, "meshtastic.connection.established")
    pub.subscribe(self.text_recv, "meshtastic.receive.text")


    # initialise telemetry values ------------------------------
  
    self.coordinates = None
    self.temperature = None


    # initialise Meshtastic node -------------------------------

    self.interface = self.find_meshtastic()		
    self.local_node = self.interface.getNode('^local')
    self.get_logger().debug(f'Current node config:{self.local_node.localConfig}')


    # ROS timers  ----------------------------------------------

    self.mesh_telemetry_timer = self.create_timer(
      60,    # send telemetry every minute
      self.send_telemetry_all
    )


    # ROS publishers -------------------------------------------

    self.text_publisher = self.create_publisher(
      MeshtasticPacket,
      "/mesh/incoming",
      10
    )

    self.telemetry_publisher = self.create_publisher(
      String,
      "/mesh/telemetry",
      10
    )


    # ROS subscribers ------------------------------------------

    self.text_subscriber = self.create_subscription(
      MeshtasticPacket,
      "/mesh/outgoing",
      self.send_text,
      10
    )

    self.gps_subscriber = self.create_subscription(
      GlobalPosition,
      "/position",    # use GPS topic for this part
      self.update_gps,
      10
    )

    self.temperature_subscriber = self.create_subscription(
      Float32,
      "/temperature",
      self.update_temp,
      10
    )


  # serial discovery ===========================================

  def find_meshtastic(self):

    while rclpy.ok():		# if running
      for port in list_ports.comports():
        if (port.serial_number == self.TARGET_SER):

          try:
            self.interface = meshtastic.serial_interface.SerialInterface()
            self.get_logger().info(f"Connected to {port.product} @ {port.device}")

            return self.interface

          except Exception as error:
            self.get_logger().warning(f"Could not open {port.device}: {error}")

      self.get_logger().warning("No Meshtastic device found. Retrying in 2 seconds...")

      time.sleep(2)


  # python pubsub callbacks ====================================

  # on serial connection ---------------------------------------

  def local_node_connected(self, interface, topic=pub.AUTO_TOPIC):
    pass


  # on text recieved -------------------------------------------

  def text_recv(self, packet, interface):

    msg = MeshtasticPacket()

    # extract key data
    msg.text = packet.get("decoded", {}).get("text")
    msg.sender = packet.get("fromId", "unknown")
    msg.channel = packet.get("channel", "unknown")
    #msg.snr = packet.get("rx_snr", "unknown")

    # set known aliases
    if msg.sender == '!a1d75c24': msg.sender = 'wayfinderMobile'
    if msg.channel == '1': msg.channel = 'wayfinder'

    print(f"From {msg.sender} on channel {msg.channel}: {msg.text}")

    self.text_publisher.publish(msg)


  # ROS callbacks ==============================================

  # send string text messages ----------------------------------

  def send_text(self, msg):
    packet = self.interface.sendText(text=msg.data, channelIndex=1)
    self.get_logger().debug(f'Sent this: {msg.data} \nVia this: {packet.channel}')


  # send all telemetry ----------------------------------------

  def send_telemetry_all(self):
    if self.coordinates is not None:    # send position
      self.get_logger().debug(f'Updated location: {self.coordinates.latitude}, {self.coordinates.longitude}, {self.coordinates.altitude}')
      self.interface.sendPosition(
        self.coordinates.latitude, 
        self.coordinates.longitude, 
        self.coordinates.altitude, 
        channelIndex=1,
        hopLimit=3)

      self.coordinates = None    # reset for clean data

    else: 
      self.get_logger().debug("No new GPS data available")


    if self.temperature is not None:    # send temperature
      self.get_logger().debug(f'Updated temperature: {self.temperature}')
      self.interface.sendText(
        text=(f'Temperature: {str(self.temperature)}'),  
        channelIndex=1,
        hopLimit=3)

      self.temperature = None    # reset for clean data

    else: 
      self.get_logger().debug("No temperature data available")

    self.interface.sendText(text="Telemetry update!", channelIndex=1)

    self.interface.sendTelemetry(channelIndex=1, hopLimit=3)

    #self.telemetry_publisher.publish(local_metrics)    # TODO: find structure of local_metrics to publish it


  # update telemetry from rover values ========================

  def update_gps(self, msg):
    self.coordinates = GlobalPosition()
    self.coordinates = msg

  def update_temp(self, msg):
    self.temperature = Float32()
    self.temperature = msg

   
def main():

  rclpy.init()

  node = MeshtasticNode()

  try:
    rclpy.spin(node)

  except KeyboardInterrupt:
    pass

  finally:
    node.interface.close()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
  main()