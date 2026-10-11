import rclpy
from rclpy.node import Node

from rover_interfaces.msg import MotorCommand


class MotorTest(Node):

  def __init__(self):
    super().__init__("motor_test")

    self.publisher = self.create_publisher(
      MotorCommand,
      "/cmd_motors",
      10
    )

    self.timer = self.create_timer(
      1.0,
      self.publish_command
    )

  def publish_command(self):
    msg = MotorCommand()

    msg.motor0 = 128
    msg.motor1 = 128

    self.publisher.publish(msg)

    self.get_logger().info(
      f"Motor command: L={msg.motor0}, R={msg.motor1}"
    )


def main():
  rclpy.init()

  node = MotorTest()

  try:
    rclpy.spin(node)
  finally:
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
  main()
