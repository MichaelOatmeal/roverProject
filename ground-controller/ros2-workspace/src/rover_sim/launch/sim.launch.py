import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ros_gz_bridge.actions import RosGzBridge
from ros_gz_sim.actions import GzServer


def generate_launch_description():
    pkg_share = get_package_share_directory('rover_sim')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    gz_spawn_model_launch_source = os.path.join(ros_gz_sim_share, 'launch', 'gz_spawn_model.launch.py')

    default_model_path = os.path.join(pkg_share, 'models', 'robot.urdf')
    bridge_config_path = os.path.join(pkg_share, 'config', 'bridge_config.yaml')
    ekf_config_path = os.path.join(pkg_share, 'config', 'ekf.yaml')
    world_path = os.path.join(pkg_share, 'world', 'my_world.sdf')

    with open(default_model_path, 'r') as infp:
        robot_desc = infp.read()

    package_parent_dir = os.path.dirname(pkg_share)
    use_sim_time = LaunchConfiguration('use_sim_time')

    set_gz_resource_path = SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=[package_parent_dir])
    set_ign_resource_path = SetEnvironmentVariable(name='IGN_GAZEBO_RESOURCE_PATH', value=[package_parent_dir])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_desc,
            'robot_description_type': 'urdf',
            'use_sim_time': use_sim_time,
        }],
    )

    gz_gui = ExecuteProcess(
        cmd=['gz', 'sim', '-g'],
        output='screen',
        condition=IfCondition(LaunchConfiguration('gui')),
    )

    gz_server = GzServer(
        world_sdf_file=world_path,
        container_name='ros_gz_container',
        create_own_container='True',
        use_composition='True',
    )

    ros_gz_bridge = RosGzBridge(
        bridge_name='ros_gz_bridge',
        config_file=bridge_config_path,
        container_name='ros_gz_container',
        create_own_container='False',
        use_composition='True',
    )

    spawn_entity = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_spawn_model_launch_source),
        launch_arguments={
            'world': 'my_world',
            'file': LaunchConfiguration('model'),
            'entity_name': 'ons_bot',
            'x': '0.0',
            'y': '0.0',
            'z': '0.1',
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
        DeclareLaunchArgument('gui', default_value='true', description='Launch the Gazebo GUI'),
        DeclareLaunchArgument('model', default_value=default_model_path, description='Absolute path to robot model file'),
        set_gz_resource_path,
        set_ign_resource_path,
        robot_state_publisher_node,
        gz_gui,
        gz_server,
        ros_gz_bridge,
        spawn_entity,
        ekf_node,
    ])