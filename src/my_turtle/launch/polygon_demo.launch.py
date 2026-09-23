import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config_file = os.path.join(
        get_package_share_directory('my_turtle'),
        'config',
        'polygon_params.yaml'
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
            executable='draw_polygon',
            name='draw_polygon',
            output='screen',
            parameters=[config_file],
        ),
        Node(
            package='my_turtle',
            executable='status_bridge',
            name='status_bridge',
            output='screen'
        )
    ])