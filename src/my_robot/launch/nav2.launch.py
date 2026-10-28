import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot')
    nav2_bringup = get_package_share_directory('nav2_bringup')

    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value=os.path.expanduser('~/ros2_ws/my_map_final.yaml'),
            description='静态地图 yaml'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_share, 'config', 'nav2_params.yaml'),
            description='Nav2 参数'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='用仿真时钟'),

        # ★ 官方 bringup：map_server + amcl + 规划 + 控制 + 代价地图 + 行为树
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_bringup, 'launch', 'bringup_launch.py')),
            launch_arguments={
                'map': map_file,
                'params_file': params_file,
                'use_sim_time': use_sim_time,
                'slam': 'False',            # ★ 必须！默认是 True（会去起 slam_toolbox）
                'autostart': 'true',
                'use_composition': 'False',  # 不合并成容器，方便调试
            }.items(),
        ),

        # ★ 我们的翻译员，也带仿真时钟
        Node(
            package='my_turtle',
            executable='cmd_vel_relay',
            name='cmd_vel_relay',
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen',
        ),
    ])
