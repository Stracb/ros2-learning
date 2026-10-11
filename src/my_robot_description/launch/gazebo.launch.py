import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot_description')

    # ① 展开 xacro，拿到 URDF 字符串
    xacro_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    # ② bridge 配置文件路径
    bridge_config = os.path.join(pkg_share, 'config', 'bridge_config.yaml')

    # ③ 起 Gazebo（复用 ros_gz_sim 自带的 launch 文件）
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': '-r empty.sdf'
        }.items(),
    )

    # ④ robot_state_publisher：把 URDF 发到 /robot_description
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
    )

    # ⑤ 把车造进 Gazebo
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'my_robot', '-z', '0.5'],
    )

    # ⑥ 启动 bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config}],
    )

    return LaunchDescription([gz_sim, rsp, spawn, bridge])