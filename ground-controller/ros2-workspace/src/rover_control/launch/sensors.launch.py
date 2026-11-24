import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
  pkg_share = os.path.join(get_package_share_directory('rover_control'))
  camera_rgb_params = os.path.join(pkg_share, 'config', 'camera.yaml')
  lidar_params = os.path.join(pkg_share, 'config', 'lidar.yaml')

  camera_rgb = Node(
    package='camera_ros',
    executable='camera_node',
    namespace='camera_rgb',
    name='camera',
    output='screen',
    parameters=[camera_rgb_params, {'use_sim_time': LaunchConfiguration('use_sim_time')}])

  # add lidar here

  return LaunchDescription([
    DeclareLaunchArgument('stamped', default_value='true'),
    DeclareLaunchArgument('use_sim_time', default_value='false'),    
    camera_rgb,
    #lidar,
  ])