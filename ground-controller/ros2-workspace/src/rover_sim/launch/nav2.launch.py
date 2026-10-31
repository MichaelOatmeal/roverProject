import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('rover_sim')
    nav2_share = get_package_share_directory('nav2_bringup')
    
    config = os.path.join(pkg_share, "config", "explore.yaml")

    use_sim_time = LaunchConfiguration('use_sim_time')

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_share, 'launch', 'navigation_launch.py')),
        launch_arguments={
            'params_file': LaunchConfiguration('nav_params_file'),
            'use_sim_time': use_sim_time,
        }.items(),
    )

    explore = Node(  # figure out how to make this work before launching
        package="explore_lite",
        name="explore_node",
        executable="explore",
        parameters=[config, {"use_sim_time": use_sim_time}],
        output="screen",
    )
 
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('nav_params_file',default_value=os.path.join(pkg_share, 'config', 'nav2_params.yaml')), 
        nav2,
    ])
