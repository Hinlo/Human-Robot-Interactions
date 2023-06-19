# Updating ROS Robot Behaviour

**Prerequisite is access to University of The West of England's Assistive Robotics Course.**

This simulation uses ros with yolo v3.

First launch the coursework container and vis studio, docker extension.
In vis studio, go \app\src\sim\scripts\sim_nav_goals.py - you can edit this and change things by restarting the sim, without restarting the container. 

***start the sim***

docker exec -it coursework bash
source /ros_entrypoint.sh
roslaunch sim sim.launch

***start yolo***

docker exec -it coursework bash
source /ros_entrypoint.sh
roslaunch darknet_ros darknet_ros.launch

***Updating the Robot Navigation Goals using VScode***
start container

go to docker tab on vs code

go to running container - apps - src - sim - click through to open sim_nav_goals.py 

Updating this should live update the course
