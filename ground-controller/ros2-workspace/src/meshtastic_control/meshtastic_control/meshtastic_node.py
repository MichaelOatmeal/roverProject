import rclpy
from rclpy.node import Node

import time

from std_msgs.msg import String

from serial.tools import list_ports

import meshtastic
import meshtastic.serial_interface

from pubsub import pub


class MeshtasticNode(Node):

  TARGET_SER = "E072A1D77B48"    # SER ID of meshtastic device over USB (via 'lsusb' command)


  def __init__(self):
    super().__init__('meshtastic_node')    # begin node

    pub.subscribe(self.local_node_connected, "meshtastic.connection.established")
    pub.subscribe(self.packet_recv, "meshtastic.receive.data")


    # initialise Meshtastic node -------------------------------

    self.interface = self.find_meshtastic()
    self.local_node = self.interface.getNode('^local')
    self.get_logger().debug(f'Current node config:{self.local_node.localConfig}')


    # ROS subscribers ------------------------------------------

    self.mesh_text_subscriber = self.create_subscription(
      String,
      "/mesh/outgoing",
      self.mesh_outgoing,
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


  # pypubsub callbacks =========================================

  # on connection
  def local_node_connected(self, interface, topic=pub.AUTO_TOPIC):
    pass

  # on packet recieved
  def packet_recv(self, interface, topic=pub.AUTO_TOPIC):
    pass


  # ROS callbacks ==============================================
  def mesh_outgoing(self, msg):
    packet = self.interface.sendText(text=msg.data, channelIndex=1)
    self.get_logger().debug(f'Sent this: {msg.data} \nVia this: {packet.channel}, id={packet.id}')



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