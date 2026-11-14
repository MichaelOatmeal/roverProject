import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
  sim_cfg = os.path.join(get_package_share_directory('rover_control'))
  default_model_path = os.path.join(sim_cfg, 'models', 'robot.urdf')
  camera_rgb_params = os.path.join(sim_cfg, 'config', 'camera.yaml')

  with open(default_model_path, 'r') as infp:
    robot_desc = infp.read()


  stamped = LaunchConfiguration('stamped')
  use_sim_time = False


  camera_rgb = Node(
    package='camera_ros',
    executable='camera_node',
    namespace='camera_rgb',
    name='camera',
    output='screen',
    parameters=[camera_rgb_params, {'use_sim_time': use_sim_time}])

  arduino_node = Node(
    package='rover_control',
    executable='arduino_node',
    name='arduino_node',
    output='screen',
    parameters=[{'use_sim_time': use_sim_time}])

  vel_translator = Node(
    package='rover_control',
    executable='vel_translator',
    name='vel_translator',
    output='screen',
    parameters=[{'use_sim_time': use_sim_time}, {'stamped': stamped}])

  ekf = Node(
    package='robot_localization',
    executable='ekf_node',
    name='ekf_filter_node',
    output='screen',
    parameters=[os.path.join(sim_cfg, 'ekf_params.yaml'), {'use_sim_time': use_sim_time}])

  robot_state_publisher_node = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    parameters=[{
      'robot_description': robot_desc,
      'robot_description_type': 'urdf',
      'use_sim_time': use_sim_time
    }],
  )

  joint_state_publisher = Node(
    package='joint_state_publisher',
    executable='joint_state_publisher',
    parameters=[{'use_sim_time': use_sim_time}]
  )

  return LaunchDescription([
    DeclareLaunchArgument('stamped', default_value='true'),
    arduino_node,
    vel_translator,
    ekf,
    robot_state_publisher_node,
    joint_state_publisher,
    camera_rgb,
  ])