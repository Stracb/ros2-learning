from launch import LaunchDescription
from launch_ros.actions import Node

import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    config_file = os.path.join(
        get_package_share_directory('my_turtle'),
        'config',
        'circle_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen'
        ),
        Node(
            package='my_turtle',
            executable='draw_circle',
            name='draw_circle',
            output='screen',
            parameters=[config_file],
        ),
    ])