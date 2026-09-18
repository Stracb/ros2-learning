from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen'
        ),
        Node(
            package='my_turtle',
            executable='draw_square',
            name='draw_square',
            output='screen',
            parameters=[{'side_length': 3.0, 'turn_speed': 0.15}],
        ),
    ])