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

### 2. Multi-Container Strategy with Shared Base Images

If you have multiple images with a lot in common (Ubuntu, ROS2, SAS, DQ Robotics, etc.), create a reusable image that includes the shared components. This image should be the base for all your other images. In this way, Docker only needs to build the common base image **once**, and the derivative images use memory on the Docker host more efficiently and load more quickly.

Let's say you need to deliver a demo using Docker Compose to `n` Docker containers. Instead of creating `n` images starting from `murilomarinho/sas:jazzy` and installing all components for each image, you can create **one common image** (e.g., `sas-base-teleoperation-demo`) for all of them. Then you create derived images starting from the common base that just copy the corresponding ROS2 packages or configuration files.

> [!IMPORTANT]
> The common image **must** be hosted in the Adorno-Lab GitHub registry (`ghcr.io/adorno-lab/`).

#### Versioning and Pinning

Images hosted in the GitHub repository are versioned. For instance, consider [`sas_unitree_b1z1_jazzy`](https://github.com/Adorno-Lab/sas_unitree_b1z1_control_template/pkgs/container/sas_unitree_b1z1_jazzy).

If you need a specific version for your derived images, you can pull by digest:

```shell
docker pull ghcr.io/adorno-lab/sas_unitree_b1z1_jazzy@sha256:b71d66fe338d2a05db7c10c78b305ffb6569901d96bcaee44180d671d66e3e0b
```

Then, use it in your Dockerfile:

```dockerfile
FROM ghcr.io/adorno-lab/sas_unitree_b1z1_jazzy@sha256:b71d66fe338d2a05db7c10c78b305ffb6569901d96bcaee44180d671d66e3e0b
```

---

#### Approach to Avoid: Several Complete Images

| Image | Components | Task |
|-------|------------|------|
| A | ROS2-Jazzy, DQ Robotics, OpenCV | State estimation |
| B | ROS2-Jazzy, DQ Robotics, Custom ROS2 interface (`my_message.msg`) | Trajectory generation |
| C | ROS2-Jazzy, DQ Robotics, RobotConstraintManager, qpOASES | Kinematic Control |
| D | ROS2-Jazzy, DQ Robotics, `sas_operator_side_receiver` | Touch X haptic device |
| E | ROS2-Jazzy, DQ Robotics, RobotConstraintManager, RobotConstraintEditor, QT | GUI |

**Problems with this approach:**
- Each image redundantly installs ROS2, DQ Robotics, and SAS
- Build times are multiplied by `n` images
- Inconsistencies may arise if base layers are updated differently
- Large total disk usage

---

#### Recommended Approach: Shared Base Image

| Image | Components | Task |
|-------|------------|------|
| `sas-base-teleoperation-demo` | **All required components** (ROS2, DQ Robotics, SAS, common libraries) | Base image (built once) |
| A | Specific ROS2 package | State estimation |
| B | Specific ROS2 package | Trajectory generation |
| C | Specific ROS2 package | Kinematic Control |
| D | Specific ROS2 package | Touch X haptic device |
| E | Specific ROS2 package | GUI |

**Benefits:**
- One image contains all shared dependencies
- Derived images are small and fast to build
- Updates to shared dependencies happen in one place
- Consistent environment across all containers

---

#### Freezing Images for Mature Demos

> [!IMPORTANT]
> Mature demos **must** have frozen Docker images. This means:
> - Derived images must start from a **specific version** (digest) of the base image
> - Use **specific tagged versions** of ROS2 packages (not `latest`) or custom libraries (e.g., RobotConstraintManager)
> - You must have a **local compressed copy** as a backup

**Create a backup with `docker save`:**

```shell
docker save ghcr.io/adorno-lab/sas-base-teleoperation-demo:latest | gzip > sas-base-teleoperation-demo.tar.gz
```

**To restore the backup:**

```shell
docker load < sas-base-teleoperation-demo.tar.gz
```

**Why this matters:**
- External registries may go offline
- Base images may be updated or removed
- Ensures the demo can always be reproduced, even years later

---

#### Checklist for Shared Base Strategy

- [ ] Common base image is built and pushed to `ghcr.io/adorno-lab/`
- [ ] Base image contains **all** shared dependencies
- [ ] Base image is tagged with a version (e.g., `v1.0.0`) and `latest`
- [ ] Derived images `FROM` the common base **using a specific digest**
- [ ] Each derived image copies only its specific package(s)
- [ ] A compressed backup (`.tar.gz`) is stored in a safe location
- [ ] Documentation lists the exact base image digest used
- [ ] CI/CD builds the common base **only** when shared dependencies change
- [ ] CI/CD builds all derived images on every commit
