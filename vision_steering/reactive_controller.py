import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class ReactiveController(Node):
    def __init__(self):
        super().__init__('reactive_controller')

        # Publisher to /cmd_vel
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscriber to /scan
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Timer to publish commands at 10 Hz
        self.timer = self.create_timer(0.1, self.publish_cmd)

        # Internal state
        self.obstacle_detected = False

    def scan_callback(self, msg: LaserScan):
        # Look at the front 10 degrees of the scan
        ranges = msg.ranges
        front = ranges[len(ranges)//2 - 5 : len(ranges)//2 + 5]

        # Detect obstacles closer than 0.5 meters
        if any(r < 0.5 for r in front if r > 0.0):
            self.obstacle_detected = True
        else:
            self.obstacle_detected = False

    def publish_cmd(self):
        twist = Twist()

        if self.obstacle_detected:
            twist.linear.x = 0.0
            twist.angular.z = 0.5   # turn left
        else:
            twist.linear.x = 0.2
            twist.angular.z = 0.3   # turn left while moving forward

        self.cmd_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = ReactiveController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
