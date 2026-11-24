import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
  use_sim_time = LaunchConfiguration('use_sim_time')
  pkg_share = get_package_share_directory('rover_control')
  default_model_path = os.path.join(pkg_share, 'models', 'robot.urdf')

  with open(default_model_path, 'r') as infp:
    robot_desc = infp.read()

  robot_state_publisher_node = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    parameters=[{
      'robot_description': robot_desc,
      'robot_description_type': 'urdf',
      'use_sim_time': use_sim_time
    }],
  )

  joint_state_publisher_node = Node(
    package='joint_state_publisher',
    executable='joint_state_publisher',
    parameters=[{'use_sim_time': use_sim_time}]
  )

  return LaunchDescription([
    DeclareLaunchArgument('stamped', default_value='true'),
    DeclareLaunchArgument('use_sim_time', default_value='false'),
    robot_state_publisher_node,
    joint_state_publisher_node,
  ])