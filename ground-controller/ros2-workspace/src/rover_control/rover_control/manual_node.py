import pygame

import rclpy
from rclpy.node import Node

from rover_interfaces.msg import MotorCommand


class KeyboardNode(Node):

  def __init__(self):
    super().__init__("keyboard_node")

    # -------------------------------------------------
    # ROS publisher
    # -------------------------------------------------

    self.motor_publisher = self.create_publisher(
      MotorCommand,
      "/cmd_motors",
      10
    )

    # -------------------------------------------------
    # Pygame setup
    # -------------------------------------------------

    pygame.init()

    self.screen = pygame.display.set_mode((500, 300))

    pygame.display.set_caption("Rover Keyboard Control")

    self.clock = pygame.time.Clock()

    # current motor command
    self.motor0 = 0
    self.motor1 = 0

    # previous motor command
    self.prev_motor0 = 0
    self.prev_motor1 = 0

    # -------------------------------------------------
    # ROS timer
    # -------------------------------------------------

    self.timer = self.create_timer(
      0.02,    # 50Hz clock
      self.update)

    self.get_logger().info("Keyboard control started")

    self.get_logger().info("W/S = forward/reverse")

    self.get_logger().info("A/D = turn")

    self.get_logger().info("Q/E = spin")

  # =====================================================
  # Keyboard update
  # =====================================================

  def update(self):

    # -------------------------------------------------
    # Process Pygame events
    # -------------------------------------------------

    for event in pygame.event.get():

      if event.type == pygame.QUIT:

        rclpy.shutdown()
        return

      if event.type == pygame.KEYDOWN:

        if event.key == pygame.K_w:
          self.motor0 = 128
          self.motor1 = 128

        elif event.key == pygame.K_s:
          self.motor0 = -128
          self.motor1 = -128

        elif event.key == pygame.K_a:
          self.motor0 = 32
          self.motor1 = 128

        elif event.key == pygame.K_d:
          self.motor0 = 128
          self.motor1 = 32

        elif event.key == pygame.K_q:
          self.motor0 = -128
          self.motor1 = 128

        elif event.key == pygame.K_e:
          self.motor0 = 128
          self.motor1 = -128

      elif event.type == pygame.KEYUP:
        self.motor0 = 0
        self.motor1 = 0


    # -------------------------------------------------
    # Publish motor command
    # -------------------------------------------------

    # only update when new command is sent
    if self.prev_motor0 != self.motor0 or self.prev_motor1 != self.motor1:

      msg = MotorCommand()

      msg.motor0 = self.motor0
      msg.motor1 = self.motor1

      self.motor_publisher.publish(msg)

    self.prev_motor0 = self.motor0
    self.prev_motor1 = self.motor1


    # -------------------------------------------------
    # Keep Pygame window responsive
    # -------------------------------------------------

    self.clock.tick(50)    # 50Hz clock

  # =====================================================
  # Shutdown
  # =====================================================

  def close(self):
    pygame.quit()


# =========================================================
# Main
# =========================================================

def main():

  rclpy.init()
  node = KeyboardNode()

  try:
    rclpy.spin(node)

  except KeyboardInterrupt:
    pass

  finally:

    node.close()

    node.destroy_node()

    if rclpy.ok():
      rclpy.shutdown()


if __name__ == "__main__":
  main()
