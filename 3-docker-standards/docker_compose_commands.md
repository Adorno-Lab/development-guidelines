# Docker Compose: build only what you changed

A demo usually runs several containers with Docker Compose (see [Multi-Container Strategy with Shared Base Images](README.md#2-multi-container-strategy-with-shared-base-images)). When you change **one** of them, rebuild **only that one**. Rebuilding every image wastes time, can pick up changes you didn't intend to deploy, and on a machine with an empty build cache can take a long time for ROS2/SAS-based images.

This guide explains which command to run depending on what you changed, and when the `--build` and `--no-cache` flags are (and are not) appropriate.

> [!NOTE]
> The examples use a Compose project with the services `state_estimation`, `kinematic_control`, and `gui`, where `kinematic_control` has `depends_on: [state_estimation]`. Replace them with the service names in your `compose.yaml` (list them with `docker compose config --services`). The `-d` flag (run in the background) is optional everywhere.

## Quick reference

| What did you change? | Command |
|---|---|
| Nothing — you just want to run the demo | `docker compose up -d` |
| Source code or config files **bind-mounted** into a container (`volumes:`) | `docker compose restart <service>` |
| The `Dockerfile` of one service, or files it `COPY`s | `docker compose up -d --no-deps --build <service>` |
| Settings in `compose.yaml` (environment, ports, volumes, command) | `docker compose up -d` |
| A remote dependency (e.g. a `git clone`d branch) **without** any change in the `Dockerfile` | Pin it (see [below](#prefer-pinning-over---no-cache)), or `docker compose build --no-cache <service>` and then `docker compose up -d --no-deps <service>` |
| The shared base image (new digest in the `FROM` line of the derived images) | `docker compose up -d --build` — this is the legitimate case for rebuilding everything |
| A service that only uses a published image (`image:` and no `build:`) | `docker compose pull <service>` and then `docker compose up -d --no-deps <service>` |

## How Compose decides what to build

| Command | What it builds | What it (re)starts |
|---|---|---|
| `docker compose up` | **Only images that don't exist yet.** Existing images are reused as they are. | Containers whose image or configuration changed |
| `docker compose up --build` | **Every** service that has a `build:` section | Containers whose image or configuration changed |
| `docker compose up --build <service>` | `<service>` **and the services it depends on** | `<service>` and its dependencies |
| `docker compose up --no-deps --build <service>` | **Only** `<service>` | **Only** `<service>` |
| `docker compose build <service>` | **Only** `<service>` | Nothing (run `docker compose up -d --no-deps <service>` afterwards) |

> [!WARNING]
> `docker compose up` **without** `--build` does **not** notice that you edited a `Dockerfile` or a file it copies. If the image already exists, Compose starts the old image. After changing a service, rebuild it explicitly, as shown in [Rebuild a single service](#rebuild-a-single-service).

Why not just always use `docker compose up --build`?

- It runs a build for **every** service. Unchanged services are mostly served from the build cache, but any service whose build context changed is rebuilt — including changes from other people that you pulled with `git pull` but didn't mean to test yet.
- If the build cache has been cleared (for example with `docker builder prune` or `docker system prune`), it rebuilds **all** images from scratch, even though working images already exist. Plain `docker compose up` would just use them.
- Naming a service is not enough: `docker compose up --build kinematic_control` also builds `state_estimation`, because `kinematic_control` depends on it. Add `--no-deps` to build and restart only the service you name.

## Rebuild a single service

**One command** — rebuild the image of one service and recreate only its container:

```shell
docker compose up -d --no-deps --build kinematic_control
```

- `--build` builds the image before starting the container.
- `--no-deps` prevents Compose from also building and recreating the services that `kinematic_control` depends on.

**Equivalent two-step version** — useful if you want to check that the build succeeds before touching the running demo:

```shell
docker compose build kinematic_control
docker compose up -d --no-deps kinematic_control
```

The other containers keep running and are not rebuilt or restarted. The same pattern is described in Docker's guide [Use Compose in production](https://docs.docker.com/compose/how-tos/production/).

## When to use `--no-cache`

Docker builds an image layer by layer and **reuses** (caches) a layer when its instruction and inputs haven't changed (see Docker's [build cache](https://docs.docker.com/build/cache/) docs). The cache is what makes a rebuild after a small change fast, so disabling it should be the exception.

The cache cannot see changes outside your build context. These instructions keep producing the **same cached layer** even when the content they download has changed:

```dockerfile
# The text of this instruction never changes, so the layer stays cached
# even after new commits are pushed to the default branch.
RUN git clone https://github.com/Adorno-Lab/robot_constraint_manager.git

# The package lists stay as they were when the layer was first built.
RUN apt-get update && apt-get install -y libeigen3-dev
```

Use `--no-cache` when:

- a layer downloads remote content that changed while the `Dockerfile` didn't, and you can't pin it (see the next section), or
- you suspect the build cache is broken (for example, a build only fails or only works on one machine).

**Always limit it to the service you need:**

```shell
# Compose: rebuild one service from scratch, then restart only that service
docker compose build --no-cache kinematic_control
docker compose up -d --no-deps kinematic_control

# Plain Docker: rebuild one image from scratch
docker build --no-cache -t kinematic_control ./kinematic_control
```

> [!CAUTION]
> Avoid `docker compose build --no-cache` and `docker compose up --build --no-cache` **without a service name**. They rebuild **every** image of the demo from scratch, which for ROS2/SAS-based images is slow and almost never necessary.

`--no-cache` rebuilds the layers of your `Dockerfile`, but it doesn't download a newer version of the base image in the `FROM` line. If you want that, add `--pull` (`docker compose build --pull <service>`). If your `FROM` line uses a digest, as recommended in [Versioning and Pinning](README.md#versioning-and-pinning), you get a newer base image by changing the digest, not with `--pull`.

### Prefer pinning over `--no-cache`

If an instruction pins exactly what it downloads, changing the pin changes the instruction. Docker then rebuilds **that layer and the ones after it** and keeps the cache for everything before it — no `--no-cache` needed:

```dockerfile
# Changing the commit hash invalidates only this layer and the ones after it.
# Replace <commit-sha> with the full hash of the commit you want.
RUN git clone https://github.com/Adorno-Lab/robot_constraint_manager.git \
    && cd robot_constraint_manager \
    && git checkout <commit-sha>
```

Pinning is also what makes images reproducible (see [Freezing Images for Mature Demos](README.md#freezing-images-for-mature-demos)).

## Changes that don't need a rebuild

- **Bind-mounted files.** If a service mounts your source code or configuration files from the host (`volumes:` in `compose.yaml`), the container already sees your edits. Restart it so the process reloads them:

  ```shell
  docker compose restart kinematic_control
  ```

- **`compose.yaml` settings** (environment variables, ports, volumes, command). Run `docker compose up -d`: Compose recreates only the containers whose configuration changed, without building anything.

## Inspect before you build

```shell
docker compose config --services   # services defined in compose.yaml
docker compose images              # images used by the project's containers
docker compose ps                  # running containers and their state
```

## Checklist

- [ ] To run the demo, use `docker compose up -d` (without `--build`)
- [ ] After changing one service, rebuild only that service: `docker compose up -d --no-deps --build <service>`
- [ ] Use `--no-cache` for **one** service, only for changed remote content or a broken cache
- [ ] Pin versions and commits in the `Dockerfile` so that `--no-cache` is rarely needed
- [ ] Rebuild all services (`docker compose up -d --build`) only when something they all share changed, such as the base image
- [ ] Use `docker compose restart <service>` for changes to bind-mounted files
