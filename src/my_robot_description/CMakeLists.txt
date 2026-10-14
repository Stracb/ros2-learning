cmake_minimum_required(VERSION 3.8)
project(my_robot_description)

find_package(ament_cmake REQUIRED)

# 把这三个目录整体装到 install/.../share/my_robot_description/ 下
install(
  DIRECTORY urdf config launch worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()