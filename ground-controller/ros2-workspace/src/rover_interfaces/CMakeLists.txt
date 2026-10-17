cmake_minimum_required(VERSION 3.8)

project(rover_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/MotorCommand.msg"
  "msg/MotorRPM.msg"
	"msg/GlobalPosition.msg"
	"msg/MeshtasticPacket.msg"
)

ament_package()
