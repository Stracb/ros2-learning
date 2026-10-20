cmake_minimum_required(VERSION 3.8)
project(my_robot)

find_package(ament_cmake REQUIRED)

# 把这三个目录整体装到 install/.../share/my_robot/ 下
install(
  DIRECTORY urdf config launch worlds rviz 
  DESTINATION share/${PROJECT_NAME}  
)

ament_package()