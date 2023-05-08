#!/usr/bin/env python3
import rospy
import math
import copy

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped

import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

class sim_nav_goals():
    def _init_(self):
        rospy.init_node('sim_nav_goals', anonymous=True)

        self.counter = 0
        
        self.client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        self.client.wait_for_server()

        rospy.Subscriber('amcl_pose', PoseWithCovarianceStamped, self.poseCallback, queue_size=10)
        
        rate = rospy.Rate(10)
        poses = [
            {'x': -1.0, 'y':  4.0, 'theta': math.pi/2, 'scan': True},
            {'x': -1.0, 'y':  4.0, 'theta': math.pi, 'scan': False},    # First pose, scan
            {'x': -6.7, 'y':  3.0, 'theta': -math.pi/2, 'scan': True},         # Second pose, scan
            {'x': -6.7, 'y':  -2.0, 'theta': 0.0, 'scan': True},
            {'x': -6.7, 'y':  -2.0, 'theta': math.pi/2, 'scan': False},       # Third pose, scan
            {'x': -4.0, 'y':  1.0, 'theta': 0.0, 'scan': False},              # Fourth pose
            {'x':  5.0, 'y':  1.0, 'theta': 0.0, 'scan': False},         # Fifth pose, scan
            {'x':  5.2, 'y': -3.0, 'theta': math.pi, 'scan': True},         # Sixth pose, scan
            {'x':  5.2, 'y': -3.0, 'theta': math.pi/2, 'scan': False},
            {'x':  6.5, 'y':  4.0, 'theta': math.pi, 'scan': True},         # Seventh pose, scan
            {'x':  0.5, 'y':  2.0, 'theta': math.pi, 'scan': True},         # Eighth pose, scan
            {'x':  0.5, 'y':  2.0, 'theta': math.pi/2, 'scan': False}, 
            {'x': -1.0, 'y':  4.0, 'theta': math.pi/2, 'scan': False},   # Return to start.
            # Currently should perform one loop then stop.
        ]
        while not rospy.is_shutdown():
            pose = poses[self.counter % len(poses)]
            self.moveToGoal(pose['x'], pose['y'], pose['theta'])

            if pose['scan'] == True:
                rospy.loginfo("Scanning")
                self.scan360(pose)
    
            
                
            self.counter += 1
            rate.sleep()

    def poseCallback(self, p):
        theta = 2*math.atan2(p.pose.pose.orientation.z, p.pose.pose.orientation.w)
        st = 'sim: Pose:x={x:.2f}m, y={y:.2f}m, yaw={th:.2f}rad'.format(x=p.pose.pose.position.x, y=p.pose.pose.position.y, th=theta)
        rospy.loginfo(st)
    
    def scan360(self, pose):
        self.moveToGoal(pose['x'], pose['y'], pose['theta'] + (2 * math.pi)/3)
        self.moveToGoal(pose['x'], pose['y'], pose['theta'] + (4* math.pi)/3)
        self.moveToGoal(pose['x'], pose['y'], pose['theta'])
        pass
    
    def moveToGoal(self, x, y, theta):
        msg = PoseStamped()
        msg.header.frame_id = 'map'
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = 0.0
        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = math.sin(theta/2)
        msg.pose.orientation.w = math.cos(theta/2)
                    
        msg.header.stamp = rospy.Time.now()
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose = msg
        self.client.send_goal(goal)
        wait = self.client.wait_for_result()
        if not wait:
            rospy.logerr("Action server is not available.")
            rospy.signal_shutdown("Action server is not available.")
        else:
            x = self.client.get_result()


        

if _name_ == '_main_':
    try:
        control = sim_nav_goals()
    except rospy.ROSInterruptException:
        pass
