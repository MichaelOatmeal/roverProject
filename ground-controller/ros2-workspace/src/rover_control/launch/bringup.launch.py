import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import UnlessCondition


def generate_launch_description():
  pkg_share = get_package_share_directory('rover_control')
  rover_sim_share = get_package_share_directory('rover_sim')

  use_sim_time = LaunchConfiguration('use_sim_time')

  # nav2 and frontier_explorer
  nav2 = IncludeLaunchDescription(
			PythonLaunchDescriptionSource(
					os.path.join(rover_sim_share, 'launch', 'nav2.launch.py')),
			launch_arguments={
					'use_sim_time': use_sim_time,
			}.items(),
	)

  # slam-toolbox and ekf
  localisation = IncludeLaunchDescription(
			PythonLaunchDescriptionSource(
					os.path.join(rover_sim_share, 'launch', 'slam.launch.py')),
			launch_arguments={
					'use_sim_time': use_sim_time,
			}.items(),
	)

  # arduino_node and vel_translator
  mcu_interface = IncludeLaunchDescription(
			PythonLaunchDescriptionSource(
					os.path.join(pkg_share, 'launch', 'mcu.launch.py')),
			launch_arguments={
					'use_sim_time': use_sim_time,
			}.items(),
	    condition=UnlessCondition(LaunchConfiguration('use_sim_time')),
	)

  # camera and lidar
  sensor_interface = IncludeLaunchDescription(
			PythonLaunchDescriptionSource(
					os.path.join(pkg_share, 'launch', 'sensors.launch.py')),
			launch_arguments={
					'use_sim_time': use_sim_time,
			}.items(),
      condition=UnlessCondition(LaunchConfiguration('use_sim_time')),

	)

	# joint+robot state publishers
  state_description = IncludeLaunchDescription(
			PythonLaunchDescriptionSource(
					os.path.join(pkg_share, 'launch', 'desc.launch.py')),
			launch_arguments={
					'use_sim_time': use_sim_time,
			}.items(),
      condition=UnlessCondition(LaunchConfiguration('use_sim_time')),
	)


  return LaunchDescription([
    DeclareLaunchArgument('stamped', default_value='true'),
    DeclareLaunchArgument('use_sim_time', default_value='false'),
    localisation,
    mcu_interface,
    sensor_interface,
    nav2,
    state_description,
  ])