# Software Design Guidelines for Experimental Setups

## Overview
This document defines the software architecture standards for experimental robotics setups in the Adorno Lab. All experimental code must follow these guidelines to ensure reproducibility, maintainability, and performance.

## 1. Technology Stack Standardization

### 1.1 Core Stack
- **ROS2 Jazzy** (LTS until 2029)
- **DQ Robotics** (for kinematics and control)
- **SAS (Smart Arm Stack)** (for robot drivers and utilities)
- **Docker** (for containerization)

### 1.2 Programming Languages
- **C++17** and **Python 3** (intersection of ROS2 Jazzy and DQ Robotics support)

### 1.3 Base Docker Images
- All containers must be based on: `murilomarinho/sas:jazzy`
- **Rationale**: Ensures identical environments across all development and deployment setups

## 2. Communication Patterns

### 2.1 ROS2 Interface Selection

| Pattern | When to Use | Examples |
|---------|-------------|----------|
| **Topics** | Continuous data streams (default) | Kinematic control loops, poses, waypoints, status updates |
| **Services** | One-time commands requiring confirmation | Calibrate camera, load file, enable motor |
| **Actions** | Long-running tasks with feedback | Execute trajectory, home robot, run calibration |

**Principle**: When in doubt, start with a topic.

### 2.2 Simulation Communication
- **DO NOT** use ZMQ Remote API with CoppeliaSim for control loops (poor performance)
- **USE** SAS with ROS2 integration in CoppeliaSim scenes
- **Alternative**: Gazebo (with justification)

## 3. Custom ROS2 Interfaces

### 3.1 Interface Design Rules
1. **Prefer standard interfaces** (from `std_msgs`, `geometry_msgs`, etc.)
   - Example: Use `std_msgs::msg::Float64MultiArray` for arrays of doubles
2. **Bundle related data** in custom messages
   - Create one message with all fields rather than multiple publishers
3. **Use `sas_msgs::Bool`** for boolean messages (not `std_msgs::Bool`)

## 4. Dependencies Management

### 4.1 Allowed Dependencies

- Open-source, well-maintained external libraries
- **Must justify** each new dependency
- **Must use minimum number** of dependencies

### 4.2 Practices to Avoid

- **Duplicate functionality** — Avoid external libraries (e.g., Boost) when the standard library or core stack already provides the same functionality
- **Custom logging** — Use `sas_datalogger` instead of building custom logging solutions
- **Unnecessary dependencies** — External libraries are allowed **only** when they provide functionality not available in the core stack
  - Must be documented
  - Must be justified in the implementation

### 4.3 Dependencies
> If a dependency duplicates functionality already available in DQ Robotics or SAS, it must be removed.

## 5. Modular Architecture

### 5.1 Node Design
- Each major component = separate ROS2 node or node composition
- One node = one well-defined task

### 5.2 Communication
- Nodes communicate **only** via ROS2 interfaces
- Shared utilities in separate libraries (no code duplication)

### 5.3 Benefits
- Parallel development
- Independent testing
- Easier debugging and profiling
- Flexible deployment (all-in-one or distributed)

## 6. Reproducibility Requirements

### 6.1 Mandatory Artifacts
Every repository must include:

- [x] `Dockerfile` (working environment)
- [x] `compose.yml` (for multi-container setups)
- [x] `README.md` with clear run instructions
- [x] Doxygen documentation for code

### 6.2 Documentation Requirements
- Document any required hardware (cameras, GPUs, robot interfaces)
- Include minimal instructions for anyone to reproduce

### 6.3 Containerization Rules
- Keep containers minimal
- Base on `murilomarinho/sas:jazzy`
- No unnecessary packages

## 7. Simulation Requirements

### 7.1 Testing Mandate
- **All** robot motion controllers must be tested in simulation before deployment

### 7.2 Simulator Options
| Simulator | Status | Communication Method |
|-----------|--------|---------------------|
| CoppeliaSim | Preferred | SAS via ROS2 (NOT ZMQ) |
| Gazebo | Allowed | ROS2 native |
| Others | Must justify | Preferable if using ROS2 |

## 8. Contributing Back

### 8.1 Upstream Contributions
- New algorithms should be contributed back to DQ Robotics/SAS when appropriate
- Builds expertise in focused toolset

## 9. Exception Handling

### 9.1 When Exceptions Are Allowed
- External libraries only when functionality **not available** in core stack
- Must be documented and justified in the implementation




