# Roadmap (to be moved to /docs)

```text
V0:
    Hardware:	      2WD, Differential steering, 3DP/Lasercut chassis
    Sensors:	      Wheel encoders, Buzzer, IMU, 
    Controllers:	  Arduino (C++),
    Modules:	      N/A

V1:
    Hardware:	      4WD, Differential steering, COTS/Lasercut chassis
    Sensors:	      Wheel encoders, Buzzer, Sonar, LED screen, 
    Controllers:	  Arduino (C++), ESP32-S3 
    Modules:	      N/A

V2:
    Hardware:	      4WD, Differential steering, Aluminum chassis
    Sensors:	      Wheel encoders, Buzzer, Sonar, LED screen, Environmental sensor suite
    Controllers:	  Arduino (C++), ESP32-S3, RasPi 4B
    Modules:	      N/A

...	etc

VF:
    Application:    Area mapping, surveillance, data collection, payload delivery, endurance missions,
    Hardware:       Aluminum chassis, AWD, AWS(?), Independent suspension 
    Sensors:        Odometry, LoRa telemetry, RTK GPS, LiDAR SLAM, Vision, Speakers, Lights
    Controllers:    Teeny 4.1 <-> ESP32 <-> RasPi, (micro)ROS2
    Modules:        Robotic arm, Drone launcher (copter), Solar
```