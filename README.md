[//]: # (This is a comment format of Markdown files!)

![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)
![License](https://img.shields.io/badge/License-GPLv3.0-green)
![Platform](https://img.shields.io/badge/Platform-Linux-orange)

# Project Overview

## What it is
Project Wayfinder is planned to be a large (roughly 0.5x0.4x0.4m) autonomous rover vehicle, designed for 3D mapping and autonomous navigation via SLAM and computer vision algorithms. Designed from the ground up, the aim is to do much as possible via ground up implementation from first principles, while learning essential frameworks such as ROS2. 

The target design architecture: RPi 5 (ROS2, autonomous nav and mapping), ESP32 (web interface and comms relay), Teensy 4.1 (microROS, real-time control)

## Status
**Focus**: Pi4 + ROS2 Simulation, assembling 4 wheel design 

 - [X] Set up ROS2 simulation
 - [O] Assemble V1 chassis
 - [O] Test cameras - OpenCV?
 - [O] Look for new SBC
 - [O] Design V1 body panels in Onshape


## License
The aim of the project is to be as open as possible, none of it is being commercialised so there's no reason to hide source code.  
See [LICENSE](/LICENSE) for more details.  

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
    ├> [Subversion Info](/_docs/versioning) 
    ├> [Electronics](/_docs/electronics)  
    └> [Hardware](/_docs/hardware)  


## Getting Started  
Check out [contributions](/CONTRIBUTING.md) before editing anything!

Wayfinder is built on *Linux* infrastructure (specifically Ubuntu 22.04, but it is compatible with 24.04 when running ROS2 Jazzy). Compilation has only been tested on `aarch64` and `x86_64` CPUs.  

- Clone this repo into your user directory and install the PlatformIO extension in your IDE
- Use the following guide to install all needed software
- Compile the packages and source the code (`source install/setup.bash`)  
- Run it! (`ros2 launch rover_sim bringup.launch.py`)

## Install Guide

Quick developer install guide for the project! This guide assumes the repo has been cloned into the user directory (~/) on an Ubuntu 22.04 install. Download commands for official software (i.e. ROS2, Gazebo, etc) have been copied from the official recommended methods, so following the authors' guide should work exactly the same.


### Install ROS2

Make sure your system is up to date before continuing  
```
sudo apt update && sudo apt upgrade
```
  
  
Enable Ubuntu universe
```
sudo apt install software-properties-common
sudo add-apt-repository universe
```

Source the ROS2 apt source
```
sudo apt update && sudo apt install curl -y
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
```


Update apt repository cache
```
sudo apt update && sudo apt upgrade
```


Install ROS2 Humble (Desktop already contains most of the needed packages)
```
sudo apt install ros-humble-desktop
rosdep update
```


Test whether your install succeeded--no errors should be thrown
```
source /opt/ros/humble/setup.bash  # should return no output
```

### Install Python virtual environment
To make the code more portable and avoid conflicts with system packages, a virtual environment is used for the python code. This should be sourced before compiling code.

Install python3-venv
```
sudo apt install python3-venv
```

Navigate to [ground-controller/python](/ground-controller/python/) and create a venv
```
cd ~/roverProject/ground-controller/python
python3 -m venv .venv
```

Enter the virtual environment and install the required modules
```
source .venv/bin/activate  # always use this to source the virtual environment
pip3 install --upgrade pip
pip3 uninstall serial  # remove serial as it overrides the needed pyserial module
pip3 install -r requirements.txt
```

### Install ROS2 packages
These are the dependencies needed for the ROS2 code to work in this repo.  
```
cd ~/roverProject/ground-controller/ros2-workspace
rosdep install --from-paths src --ignore-src -r -y
```

...Or you could install the packages manually via apt
```
sudo apt install \
    ros-$ROS_DISTRO-navigation2 \
    ros-$ROS_DISTRO-nav2-bringup \
    ros-$ROS_DISTRO-slam-toolbox \
```


### Install Gazebo
Simulator to test sensors/tuning before pushing to production hardware

Make sure the system is up to date
```
sudo apt update
sudo apt install curl lsb-release gnupg
```

Source apt repository and install Gazebo
```
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt update
sudo apt install gz-harmonic
```