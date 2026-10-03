[//]: # (This is a comment format of Markdown files!)

![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux-orange)

# Project Overview

## What it is
Project Wayfinder is planned to be a relatively large (exact size TBD) autonomous rover vehicle, designed for 3D mapping and autonomous navigation via SLAM and computer vision algorithms. Designed from the ground up, the aim is to do much as possible via ground up implementation from first principles, while learning essential frameworks such as ROS2. 

The target design architecture: RasPi 4 (ROS2, autonomous nav and mapping), ESP32 (web interface and comms relay), Teensy 4.1 (microROS, real-time control)

## File Index

**[Arduino](/arduino)**  
    ├> [Local libraries](/arduino/lib)  
    ├> [Source Code](/arduino/src)  
    └> [Header files](/arduino/include)  

**[Ground Controller](/ground-controller)**  
		├> [ROS2](/ground-controller/ros2-workspace)
    └> [Python](/ground-controller/python) (via PyGame & PySerial)

**[Docs](/_docs)**  
    ├> [Assets](/_docs/assets)  
    ├> [Subversion Info](/_docs/versioning) (complete breakdowns of each subversion)  
    ├> [Electronics](/_docs/electronics)  
    └> [Hardware](/_docs/hardware)  


## Getting Started  
Check out [contributions](/CONTRIBUTING.md) before editing anything!

Wayfinder is built mainly on *Linux* infrastructure (specifically Ubuntu 22.04); alternatives will be mentioned where possible.  

- Clone this repo and install the PlatformIO extension in your IDE
- Follow the [ROS2 "Humble" install guide](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)


## Status
**Focus**: Arduino + ROS2 fundamentals, test rig development  

 - [X] Set up dev environment (ROS2 Humble, PlatformIO, Git)
 - [X] Finalize parts list for first purchase
 - [X] Serial communication, PWM motor control, encoder reading
 - [ ] ROS2 practice: Publisher/subscriber nodes, serial communication
 - [X] Design V0 test rig in Onshape


## Team & Credits
Project Lead - Michael Yakubu  
Hardware Design - Faisal Ibrahim, Yahia Eltahir  
Software Engineering - TBD  
Electronics Design - TBD  

### License
See [LICENSE](/LICENSE) for more details.  