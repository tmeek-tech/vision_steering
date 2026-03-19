#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class ColorDetectorNode(Node):
    def __init__(self):
        super().__init__('color_detector')
        
        # Publisher to /cmd_vel
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscriber to /scan
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Internal state
        self.obstacle_detected = False
        self.position = 'none'

        # Timer to publish commands at 10 Hz
        self.timer = self.create_timer(0.1, self.publish_cmd)

        self.bridge = CvBridge()

        # Change this if your camera topic is different.
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.get_logger().info('Color detector node started.')

    def image_callback(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            return

        # Convert BGR image to HSV for easier color thresholding.
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detect RED using two HSV ranges because red wraps around the hue wheel.
        lower_red_1 = np.array([0, 120, 70])
        upper_red_1 = np.array([10, 255, 255])

        lower_red_2 = np.array([170, 120, 70])
        upper_red_2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
        mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
        mask = mask1 | mask2

        # Clean up noise a little.
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        height, width = frame.shape[:2]
        image_center_x = width // 2

        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            # Ignore tiny blobs.
            if area > 300:
                x, y, w, h = cv2.boundingRect(largest)
                centroid_x = x + w // 2

                # Decide rough position in the image.
                tolerance = width * 0.1
                if centroid_x < image_center_x - tolerance:
                    self.position = 'left'
                elif centroid_x > image_center_x + tolerance:
                    self.position = 'right'
                else:
                    self.position = 'center'

                # self.get_logger().info(
                #     f'Red object detected: {self.position} | area={area:.1f} | centroid_x={centroid_x}'
                # )

                # Draw helpful overlays for debugging.
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (centroid_x, y + h // 2), 5, (255, 0, 0), -1)
                cv2.line(frame, (image_center_x, 0), (image_center_x, height), (255, 255, 0), 2)
                cv2.putText(
                    frame,
                    f'Position: {self.position}',
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2
                )
        # else:
        #     self.get_logger().info('No red object detected.')

        cv2.imshow('Camera View', frame)
        cv2.imshow('Red Mask', mask)
        cv2.waitKey(1)

    def scan_callback(self, msg: LaserScan):
        # Look at the front 10 degrees of the scan
        ranges = msg.ranges
        front = ranges[len(ranges)//2 - 5 : len(ranges)//2 + 5]
        
        # self.get_logger().info(
        #     f'hello from scan callback'
        # )

        # Detect obstacles closer than 0.5 meters
        if any(r < 0.5 for r in ranges if r > 0.0):
            self.obstacle_detected = True
        else:
            self.obstacle_detected = False
            

    def publish_cmd(self):
        twist = Twist()

        twist.linear.x = 0.0
        twist.angular.z = 0.0
        if not self.obstacle_detected:
            if self.position == 'right':
                twist.angular.z = -0.3   # turn right
            elif self.position == 'left':
                twist.angular.z = 0.3   # turn left
            elif self.position == 'center':
                twist.linear.x = 0.2

        self.cmd_pub.publish(twist)

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ColorDetectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
