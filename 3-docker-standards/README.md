# Docker Standards

Docker best practices for building, running, and maintaining containerized ROS2 applications in the Adorno Lab RAICo1-based projects.

---

## Core Principles

1. **Reproducibility** — Anyone should be able to build and run your container with minimal instructions
2. **Minimalism** — Keep images small, secure, and fast to build
3. **Consistency** — All containers use the same base images and/or patterns
4. **Security** — Follow least-privilege principles and keep dependencies updated

---

## Quick Start

### 1. Base Image

All containers that require SAS **must** be based on:

```dockerfile
FROM murilomarinho/sas:jazzy
```


## Tips from Official Docker Documentation

These tips are adapted directly from Docker's official [Building best practices](https://docs.docker.com/build/building/best-practices/) guide. Following them ensures your images are secure, efficient, and maintainable.


### Base Images & Layers

| Tip | Why It Matters |
|-----|----------------|
| **Choose minimal base images** | Smaller images = faster downloads, less disk space, fewer vulnerabilities. |
| **Pin base image versions** | Use specific tags (e.g., `jazzy`) and consider **digests** (e.g., `image@sha256:...`) for full supply chain integrity. |
| **Use multi-stage builds** | Separate build tools from runtime; final image contains only what's needed to run. |
| **Create reusable stages** | If you have multiple images with common components, base them on a shared stage to save build time and memory. |
