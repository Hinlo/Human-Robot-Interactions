#!/usr/bin/env python3
import rospy
import math
import copy
import time
import threading

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from object_recognition_msgs.msg import ObjectType
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from darknet_ros_msgs.msg import BoundingBoxes

isFound = False

class sim_nav_goals():
    def __init__(self):
        rospy.init_node('sim_nav_goals', anonymous=True)
        self.thresh = 0.6
        self.counter = 0
        self.loop_counter = 0
        self.max_loop = 3
        
        self.client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        self.client.wait_for_server()

        rospy.Subscriber('amcl_pose', PoseWithCovarianceStamped, self.poseCallback, queue_size=10)
        rospy.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes, self.ImageCallback, queue_size=10)
        
        self.rate = rospy.Rate(10)

        self.posThread()
        

    def posThread(self):
        
        
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

        pose = poses[0]
        self.moveToGoal(pose['x'], pose['y'], pose['theta'])
        
        print("Please Choose Object To Find")
        print("Press Enter Key To select")
        key = input()
        
        while not rospy.is_shutdown() and self.loop_counter < self.max_loop:

            global isFound

            if isFound == True:
                print("_________________BOTTLE SO MUST STOP___________________")
                print("Press Enter Key To Stop Alarm")
                key = input()
                pose = poses[0]
                self.moveToGoal(pose['x'], pose['y'], pose['theta'])
                while not rospy.is_shutdown():
                    pass
            else:

                pose = poses[self.counter % len(poses)]
                self.moveToGoal(pose['x'], pose['y'], pose['theta'])

                if pose['scan'] == True:
                    rospy.loginfo("Scanning")
                    self.scan360(pose)
            
                    
                self.counter = (self.counter + 1) % len(poses)
                if(self.counter == 0):
                    self.loop_counter += 1
                
                if self.loop_counter == self.max_loop:
                    print("Maximum Loops Done. \n Returning Home")
                    pose = poses[0]
                    self.moveToGoal(pose['x'], pose['y'], pose['theta'])
                    while not rospy.is_shutdown():
                        print("Finished Loops. Not Found Item")
                        time.sleep(1)

            self.rate.sleep()

    def poseCallback(self, p):
        theta = 2*math.atan2(p.pose.pose.orientation.z, p.pose.pose.orientation.w)
        st = 'sim: Pose:x={x:.2f}m, y={y:.2f}m, yaw={th:.2f}rad'.format(x=p.pose.pose.position.x, y=p.pose.pose.position.y, th=theta)
        rospy.loginfo(st)
    
    def bottleFound(self):
        global isFound
        if isFound == False:
            print("----------- STOPING THE ROBOT -------------------")
        self.client.cancel_all_goals()
        time.sleep(0.01)
        isFound = True
        time.sleep(0.01)
    
    def scan360(self, pose):
        self.moveToGoal(pose['x'], pose['y'], pose['theta'] + (2 * math.pi)/3)
        self.moveToGoal(pose['x'], pose['y'], pose['theta'] + (4* math.pi)/3)
        self.moveToGoal(pose['x'], pose['y'], pose['theta'])
        pass

    def ImageCallback(self, msg):
        inmsg = msg.bounding_boxes
        #print(inmsg)
        for i in range(len(inmsg)):
            if inmsg[i].Class == "bottle":
                # print("found Botte")
                if inmsg[i].probability > self.thresh:
                    # print("yep Thats a bottle")
                    self.bottleFound()
    

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


        

if __name__ == '__main__':
    try:
        control = sim_nav_goals()
    except rospy.ROSInterruptException:
        pass
