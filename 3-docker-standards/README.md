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




