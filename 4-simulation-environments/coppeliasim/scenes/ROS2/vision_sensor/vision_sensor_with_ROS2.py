import math
import re
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo


def sanitize_name(name: str) -> str:
    """Make a string safe for use as a ROS 2 node/topic/frame component."""
    clean = re.sub(r'[^A-Za-z0-9_]', '_', name)
    clean = clean.strip('_')
    if clean and clean[0].isdigit():
        clean = '_' + clean
    return clean or 'sensor'


class CameraPublisher(Node):
    """Publishes a CoppeliaSim vision sensor as sensor_msgs/Image + CameraInfo."""

    def __init__(self, node_name: str, frame_id: str,
                 image_topic: str, info_topic: str):
        super().__init__(node_name)
        self.frame_id = frame_id
        self.image_pub = self.create_publisher(
            Image, image_topic, qos_profile_sensor_data)
        self.info_pub = self.create_publisher(
            CameraInfo, info_topic, qos_profile_sensor_data)

    def publish(self, rgb: bytes, width: int, height: int, fov: float, sim_time: float):
        stamp = rclpy.time.Time(seconds=sim_time).to_msg()

        # CoppeliaSim returns rows bottom-to-top; ROS expects top-to-bottom.
        frame = np.frombuffer(rgb, dtype=np.uint8).reshape(height, width, 3)
        frame = np.flipud(frame)

        img = Image()
        img.header.stamp = stamp
        img.header.frame_id = self.frame_id
        img.height = height
        img.width = width
        img.encoding = 'rgb8'
        img.is_bigendian = 0
        img.step = width * 3
        img.data = frame.tobytes()
        self.image_pub.publish(img)

        # Pinhole intrinsics. CoppeliaSim's perspective angle applies to the larger image side.
        f = (max(width, height) / 2.0) / math.tan(fov / 2.0)
        info = CameraInfo()
        info.header = img.header
        info.height = height
        info.width = width
        info.distortion_model = 'plumb_bob'
        info.d = [0.0, 0.0, 0.0, 0.0, 0.0]
        info.k = [f, 0.0, width / 2.0,
                  0.0, f, height / 2.0,
                  0.0, 0.0, 1.0]
        info.r = [1.0, 0.0, 0.0,
                  0.0, 1.0, 0.0,
                  0.0, 0.0, 1.0]
        info.p = [f, 0.0, width / 2.0, 0.0,
                  0.0, f, height / 2.0, 0.0,
                  0.0, 0.0, 1.0, 0.0]
        self.info_pub.publish(info)


def sysCall_init():
    sim = require('sim')

    self.node = None
    self.ros_initialized = False
    try:
        # The script is a child object of the vision sensor.
        # ".." returns the parent of the script object, which is the sensor itself.
        self.sensor = sim.getObject('..')

        # Confirm it is a vision sensor by reading a vision-specific parameter.
        # This will raise if the object is not a vision sensor.
        self.fov = sim.getObjectFloatParam(
            self.sensor, sim.visionfloatparam_perspective_angle)

        # Alias is the name shown in the scene hierarchy, e.g. "cam_sensor_1"
        alias = sim.getObjectAlias(self.sensor)
        base = sanitize_name(alias)

        node_name   = f'coppeliasim_camera_{base}'
        frame_id    = base
        image_topic = f'camera/{base}/image_raw'
        info_topic  = f'camera/{base}/camera_info'

        if not rclpy.ok():
            rclpy.init()
            self.ros_initialized = True

        self.node = CameraPublisher(
            node_name=node_name,
            frame_id=frame_id,
            image_topic=image_topic,
            info_topic=info_topic,
        )
        print(f"ROS 2 camera publisher initialized "
              f"(sensor='{alias}', image_topic='{image_topic}', "
              f"info_topic='{info_topic}')")
    except Exception as e:
        print(f"Error initializing ROS 2: {e}")


def sysCall_sensing():
    if self.node is None:
        return
    sim = require('sim')
    # Vision sensors are already handled by the time sensing runs
    rgb, (width, height) = sim.getVisionSensorImg(self.sensor)
    self.node.publish(rgb, width, height, self.fov, sim.getSimulationTime())
    rclpy.spin_once(self.node, timeout_sec=0.0)


def sysCall_cleanup():
    if self.node is not None:
        self.node.destroy_node()
        self.node = None
    if self.ros_initialized:
        rclpy.shutdown()
        self.ros_initialized = False
    print("ROS 2 cleaned up")