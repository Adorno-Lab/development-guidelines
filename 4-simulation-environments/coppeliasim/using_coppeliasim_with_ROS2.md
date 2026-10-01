# ROS2 with CoppeliaSim

## Set your Python environment

In the `usrset.txt` file, set the Python path. Ensure you have ROS2 and SAS installed on your system.

<img width="800" alt="image" src="https://github.com/user-attachments/assets/f601cad1-6ce8-4e91-b6a6-fa9b1d2e2f10" />


> [!TIP]
> To know where your `usrset.txt` file is, type this in the Lua commander
> ```shell
> sim.getStringParam(sim.stringparam_usersettingsdir)
> ```

> [!NOTE]
> In this example, we use a virtual environment to install the dependencies.
>
> Create a virtual environment
>
> ```shell
> cd ~
> python3 -m venv coppeliasim_venv
> ```
> 
> Activate the venv
> ```shell
> cd ~
> source coppeliasim_venv/bin/activate
> ```
>
> Install dependencies
>
>
> ```shell
> python3 -m pip install pyzmq cbor2 dqrobotics setuptools pyyaml numpy
> ```

> [!IMPORTANT]
> Create the venv with the same Python version used by your ROS2 distribution (e.g., Python 3.12 for ROS2 Jazzy on Ubuntu 24.04). Otherwise, `rclpy` cannot be imported.

Now, modify the `usrset.txt` file to 

```text
defaultPython = /home/<your-user>/coppeliasim_venv/bin/python3 // e.g. c:/Python38/python.exe
```

## Launch CoppeliaSim

The Python scripts import `rclpy`, which is provided by ROS2 and not by the venv. Therefore, launch CoppeliaSim from a terminal where ROS2 is sourced. If you launch it from a desktop icon or a file manager, the scripts fail with `ModuleNotFoundError: No module named 'rclpy'`.

```shell
source /opt/ros/jazzy/setup.bash
cd ~/Downloads/CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu24_04
./coppeliaSim.sh
```


## Examples

### Vision sensor

To publish vision sensor data in CoppeliaSim to a ROS2 topic, add a non-threaded Python script as a child of the vision sensor. The vision sensor's name will be used as the topic name. Therefore, choose a unique name in `snake_case` format

<img width="800" alt="Screenshot from 2026-09-29 14-01-02" src="https://github.com/user-attachments/assets/196b1d39-3446-4fc4-a7ed-61f8cf909aa5" />

Edit the Python script according to this file [vision_sensor_with_ROS2.py](https://github.com/Adorno-Lab/development-guidelines/blob/main/4-simulation-environments/coppeliasim/scenes/ROS2/vision_sensor/vision_sensor_with_ROS2.py)

Full scene available here: [vision_sensor_with_ROS2.ttt](https://github.com/Adorno-Lab/development-guidelines/blob/main/4-simulation-environments/coppeliasim/scenes/ROS2/vision_sensor/vision_sensor_with_ROS2.ttt)


### Holonomic mobile platform

This example shows how to command a holonomic mobile platform in CoppeliaSim using a ROS2 topic. Tested with CoppeliaSim 4.7.0 rev4 and ROS2 Jazzy.

<img width="800"  alt="Screenshot from 2026-10-01 11-50-38" src="https://github.com/user-attachments/assets/8f5a4346-4c85-433b-9837-d41de7670df4" />

The script `holonomic_cmd` (child of `trunk_respondable`) subscribes to a `geometry_msgs/msg/TwistStamped` topic and maps `twist.linear.x`, `twist.linear.y`, and `twist.angular.z` to the wheel velocities.

Start the simulation and, in a terminal with ROS2 sourced, publish a command:

```shell
ros2 topic pub -r 20 /sas_b1/b1_1/set/holonomic_target_twist geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.05, y: 0.05}, angular: {z: 0.2}}}"
```

> [!NOTE]
> The base stops if no command arrives for 0.5 s (`CMD_TIMEOUT_SEC` in the script). Therefore, publish continuously (`-r 20`). Press `Ctrl+C` to stop the base.

> [!NOTE]
> The twist is expressed in the base frame, in m/s and rad/s. For instance, `x: 0.1` drives the base forward at 0.1 m/s. The compensating factors in the script are derived from the wheel geometry: `LINEAR_GAIN = 1/r` and `ANGULAR_GAIN = (lx + ly)/r`, where `r = 0.05 m` is the wheel radius, and `lx = 0.228 m` and `ly = 0.1585 m` are the distances from the base center to the wheels along the x-axis and y-axis, respectively.

To check that the scene is subscribed to the topic (`coppeliasim_holonomic_base` should appear as a subscriber):

```shell
ros2 topic info -v /sas_b1/b1_1/set/holonomic_target_twist
```

The script also publishes the measured twist of the base on `/sas_b1/b1_1/get/holonomic_twist` (`geometry_msgs/msg/TwistStamped`) after every simulation step. It uses the same fields and units as the command, expressed in the base frame (`header.frame_id` is `trunk_respondable`), so you can compare both directly:

```shell
ros2 topic echo /sas_b1/b1_1/get/holonomic_twist
```

> [!TIP]
> In CoppeliaSim 4.7, the path `'.'` refers to the script object itself, not to the object it is attached to. That is why the script uses `ROBOT_BASE_PATH = '..'` to get the robot base.

Edit the Python script according to this file [holonomic_cmd.py](https://github.com/Adorno-Lab/development-guidelines/blob/main/4-simulation-environments/coppeliasim/scenes/ROS2/holonomic_base/holonomic_cmd.py)

Scene available here: [holonomic_b1.ttt](https://github.com/Adorno-Lab/development-guidelines/blob/main/4-simulation-environments/coppeliasim/scenes/ROS2/holonomic_base/holonomic_b1.ttt)


