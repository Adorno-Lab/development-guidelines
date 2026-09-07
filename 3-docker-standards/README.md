# Docker Standards

Docker best practices for building, running, and maintaining containerized ROS2 applications in the Adorno Lab RAICo1-based projects. These tips are adapted directly from Docker's official [Building best practices](https://docs.docker.com/build/building/best-practices/) guide. Following them ensures your images are secure, efficient, and maintainable.



## Core Principles

1. **Reproducibility** — Anyone should be able to build and run your container with minimal instructions
2. **Minimalism** — Keep images small, secure, and fast to build
3. **Consistency** — All containers use the same base images and/or patterns


## Quick Start

### 1. Base Image

Ensure your base image is from a trusted source. For instance, all containers that require SAS **must** be based on:

```dockerfile
FROM murilomarinho/sas:jazzy
```

### 2. Common Images

If you have multiple images with a lot in common (Ubuntu, ROS2, SAS, DQ Robotics, etc), create a reusable image that includes the shared components. This image should be the base for all your other images. In this way, Docker only needs to build the common base image once, and the derivative images use memory on the Docker host more efficiently and load more quickly.

Let's say you need to deliver a demo using Docker Compose to run three Docker containers. Instead of creating three images starting from `murilomarinho/sas:jazzy`, in which you install all components for each image, you can create one common image for all of them. Then, you can have derived images starting from the common base that just copy the corresponding ROS2 packages or configuration files.

| Image | Component | Task |
|-------|-----------|-------|
| A. | ROS2-Jazzy, DQ Robotics, OpenCV | State estimation |
| B. | ROS2-Jazzy, DQ Robotics, Custom ROS2 interface (my_mesage.msg) | Trajectory generation |
| C. | ROS2-Jazzy, DQ Robotics, RobotConstraintManager, qpOASES | Kinematic Control|
| D. | ROS2-Jazzy, DQ Robotics, sas_operator_side_receiver| Touch X haptic device |
| E. | ROS2-Jazzy, DQ Robotics, RobotConstraintManager, RobotConstraintEditor, QT | GUI|




