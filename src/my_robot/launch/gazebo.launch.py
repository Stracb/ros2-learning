import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot')

    # ① 展开 xacro，拿到 URDF 字符串
    xacro_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    # ② 三个路径
    bridge_config = os.path.join(pkg_share, 'config', 'bridge_config.yaml')
    world_file = os.path.join(pkg_share, 'worlds', 'my_world.sdf')
    rviz_config = os.path.join(pkg_share, 'rviz', 'my_robot.rviz')
    controller_config = os.path.join(pkg_share, 'config', 'ros2_control.yaml')

    # ③ 起 Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': '--render-engine-gui ogre --render-engine-server ogre2 -r ' + world_file
        }.items(),
    )

    # ④ robot_state_publisher
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

    # ⑥ 桥接（/clock 和 /scan）
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config}],
    )

    # ⑦ 两个控制器 spawner
    jsb_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--param-file', controller_config],
    )
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--param-file', controller_config],
    )

    # ⑧ 可选 RViz
    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz', default_value='true',
        description='是否同时启动 RViz2（true / false）')
    use_rviz = LaunchConfiguration('use_rviz')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription([
        declare_use_rviz,

        # ★ 事件监听必须在 spawn 之前注册
        RegisterEventHandler(OnProcessExit(
            target_action=spawn, on_exit=[jsb_spawner])),
        RegisterEventHandler(OnProcessExit(
            target_action=jsb_spawner, on_exit=[diff_drive_spawner])),

        gz_sim, rsp, spawn, bridge, rviz,
    ])