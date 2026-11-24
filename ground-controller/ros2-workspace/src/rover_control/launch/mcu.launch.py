import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

  stamped = LaunchConfiguration('stamped')

  arduino_node = Node(
    package='rover_control',
    executable='arduino_node',
    name='arduino_node',
    output='screen')

  vel_translator = Node(
    package='rover_control',
    executable='vel_translator',
    name='vel_translator',
    output='screen',
    parameters=[{'stamped': stamped}])

  return LaunchDescription([
    DeclareLaunchArgument('stamped', default_value='true'),
    DeclareLaunchArgument('use_sim_time', default_value='false'),
    arduino_node,
    vel_translator
  ])