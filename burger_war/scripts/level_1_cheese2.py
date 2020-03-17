#!/usr/bin/env python
# -*- coding: utf-8 -*-

# level_1_cheese1.py
# RESPECT yamaguchi takuya @dashimaki360
# edit by tanaka yoshiki


import rospy
import random

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState

class CheeseBurger():
    def __init__(self, bot_name):
        # bot name 
        self.name = bot_name
        # robot state 'gogo' or 'back'
        self.state = 'go' 
        # robot wheel rot 
        self.wheel_rot_r = 0
        self.wheel_rot_l = 0
        self.pose_x = 0
        self.pose_y = 0

        # speed [m/s]
        self.speed = 0.5

        # publisher
        self.vel_pub = rospy.Publisher('cmd_vel', Twist,queue_size=1)
        # subscriber
        self.odom_sub = rospy.Subscriber('odom', Odometry, self.odomCallback)
        self.odom_sub = rospy.Subscriber('joint_states', JointState, self.jointstateCallback)

    def odomCallback(self, data):
        '''
        Dont use odom in this program now
        update robot pose in gazebo
        '''
        self.pose_x = data.pose.pose.position.x
        self.pose_y = data.pose.pose.position.y

    def jointstateCallback(self, data):
        '''
        update wheel rotation num
        '''
        self.wheel_rot_r = data.position[0]
        self.wheel_rot_l = data.position[1]

    def calcTwist(self):
        '''
        calc twist from self.state
        'go' -> self.speed,  'back' -> -self.speed
        '''
        if self.state == 'go':
            # set speed x axis
            x = self.speed
            twist = Twist()
            twist.linear.x = x; twist.linear.y = 0; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0

        elif self.state == 'back':
            # set speed x axis
            x = -2 * self.speed
            c = x*0.1
            twist = Twist()
            twist.linear.x = c; twist.linear.y = 0; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 2*3.14/c
            c = c+0.1

        else:
            # error state
            x = 0            
            twist = Twist()
            twist.linear.x = x; twist.linear.y = 0; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
            rospy.logerr("SioBot state is invalid value %s", self.state)


        return twist

    def calcState(self):
        '''
        update robot state 'go' or 'back'
        '''
        if self.state == 'go' and self.wheel_rot_r > 27:
            self.state = 'back'
        elif self.state == 'back' and self.wheel_rot_r < 1:
            self.state = 'go'

    def strategy(self):
        '''
        calc Twist and publish cmd_vel topic
        Go and Back loop forever
        '''
        r = rospy.Rate(5) # change speed 1fps

        while not rospy.is_shutdown():
            # update state from now state and wheel rotation
            self.calcState()
            # update twist
            twist = self.calcTwist()

            # publish twist topic
            self.vel_pub.publish(twist)

            r.sleep()


if __name__ == '__main__':
    rospy.init_node('enemy')
    bot = CheeseBurger('mybot')
    bot.strategy()

