import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('rover_sim')
    slam_share = get_package_share_directory('slam_toolbox')
    ekf_config_path = os.path.join(pkg_share, 'config', 'ekf.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')


    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_share, 'launch', 'online_async_launch.py')),
        launch_arguments={
            'slam_params_file': LaunchConfiguration('slam_params_file'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items(),
    )

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_path, {'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=os.path.join(pkg_share, 'config', 'slam_params.yaml')),
        slam,
        ekf_node,
    ])