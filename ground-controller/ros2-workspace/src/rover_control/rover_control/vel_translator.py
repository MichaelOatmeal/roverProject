import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped
from rover_interfaces.msg import MotorCommand


class CmdVelToMotors(Node):

  def __init__(self):
    super().__init__('cmd_vel_to_motors')
    self.declare_parameter('wheel_radius', 0.05)
    self.declare_parameter('track_width', 0.23)
    self.declare_parameter('max_rpm', 251.0)
    self.declare_parameter('timeout', 0.5)           # seconds without a command
    self.declare_parameter('stamped', True)          # False on Humble

    self.radius = self.get_parameter('wheel_radius').value
    self.width = self.get_parameter('track_width').value
    self.max_rpm = self.get_parameter('max_rpm').value
    self.timeout = self.get_parameter('timeout').value
    self.stamped = self.get_parameter('stamped').value

    self.vel = self.w = 0.0
    self.last_cmd = self.get_clock().now()

    msg_type = TwistStamped if self.stamped else Twist
    
    self.sub = self.create_subscription(
      msg_type, 
      '/cmd_vel', 
      self.on_cmd, 
      10)
    
    self.pub = self.create_publisher(
      MotorCommand, 
      '/cmd_motors', 
      10)
    
    self.timer = self.create_timer(
      0.05,  # 20Hz
      self.tick)

  def on_cmd(self, msg):
    twist = msg.twist if self.stamped else msg
    self.vel = twist.linear.x
    self.w = twist.angular.z
    self.last_cmd = self.get_clock().now()

  def tick(self):
    age = (self.get_clock().now() - self.last_cmd).nanoseconds * 1e-9
    vel, w = (self.vel, self.w) if age < self.timeout else (0.0, 0.0)

    vel_l = vel - w * self.width / 2.0
    vel_r = vel + w * self.width / 2.0
    conversion = 60.0 / (2.0 * math.pi * self.radius)  # m/s -> RPM
    
    rpm_l = vel_l * conversion 
    rpm_r = vel_r * conversion

    peak = max(abs(rpm_l), abs(rpm_r))
    
    if peak > self.max_rpm:
      rpm_l = rpm_l * self.max_rpm / peak 
      rpm_r = rpm_r * self.max_rpm / peak

    out = MotorCommand()
    out.motor0 = int(round(rpm_l))
    out.motor1 = int(round(rpm_r))
    self.pub.publish(out)

  def kill(self):
    out = MotorCommand()
    out.motor0 = out.motor1 = 0
    self.pub.publish(out)      


def main():
  
  rclpy.init()
  node = CmdVelToMotors()
  
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass
  finally:
    node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()

if __name__ == "__main__":
  main()