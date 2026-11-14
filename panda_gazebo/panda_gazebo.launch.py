import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

HERE = os.path.dirname(os.path.abspath(__file__))
XACRO = os.path.join(HERE, 'panda_gazebo.urdf.xacro')


def generate_launch_description():
    robot_desc = ParameterValue(Command(['xacro ', XACRO]), value_type=str)

    return LaunchDescription([
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', 'empty.sdf',
                 '--physics-engine', 'gz-physics-bullet-featherstone-plugin'],
            output='screen'
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
            output='screen'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc, 'use_sim_time': True}],
            output='screen'
        ),
        TimerAction(period=3.0, actions=[
            Node(package='ros_gz_sim', executable='create',
                 arguments=['-topic', 'robot_description', '-name', 'panda', '-z', '0.01'],
                 output='screen'),
        ]),
        TimerAction(period=8.0, actions=[
            Node(package='controller_manager', executable='spawner',
                 arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
                 output='screen'),
        ]),
        TimerAction(period=12.0, actions=[
            Node(package='controller_manager', executable='spawner',
                 arguments=['panda_arm_controller', '--controller-manager', '/controller_manager'],
                 output='screen'),
        ]),
        TimerAction(period=16.0, actions=[
            Node(package='controller_manager', executable='spawner',
                 arguments=['panda_hand_controller', '--controller-manager', '/controller_manager'],
                 output='screen'),
        ]),
    ])
