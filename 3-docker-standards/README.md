# Docker Standards

Docker best practices for building, running, and maintaining containerized ROS2 applications in the Adorno Lab RAICo1-based projects.

---

## 📋 Core Principles

1. **Reproducibility** — Anyone should be able to build and run your container with minimal instructions
2. **Minimalism** — Keep images small, secure, and fast to build
3. **Consistency** — All containers use the same base images and/or patterns
4. **Security** — Follow least-privilege principles and keep dependencies updated

---

## 🚀 Quick Start

### 1. Base Image

All containers that require SAS **must** be based on:

```dockerfile
FROM murilomarinho/sas:jazzy
```