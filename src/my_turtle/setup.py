from setuptools import find_packages, setup

package_name = 'my_turtle'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/square_params.yaml']),
        ('share/' + package_name + '/launch', ['launch/square_demo.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pummy',
    maintainer_email='pummy@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'draw_circle = my_turtle.draw_circle:main',
            'draw_line = my_turtle.draw_line:main',
            'read_pose = my_turtle.read_pose:main',
            'pubsub = my_turtle.pubsub:main',
            'greeter = my_turtle.greeter:main',
            'turtle_control = my_turtle.turtle_control:main',
            'draw_square = my_turtle.draw_square:main',
            'move_client = my_turtle.move_client:main',
            'rotate_client = my_turtle.rotate_client:main',
            'my_rotate_server = my_turtle.my_rotate_server:main',
            
        ],
    },
)
