## Prerequisites

Before setting up the workflow below, make sure of the following:

1. **A working `Dockerfile` already committed to the repository**, at whatever path you choose (e.g. `path_to_your_image/Dockerfile`). You'll reference this path in the workflow's `DOCKERFILE_PATH` variable.

2. **Enable write permissions for the workflow's `GITHUB_TOKEN`.** In the repository (not organization) settings, go to **Settings → Actions → General → Workflow permissions**, select **"Read and write permissions"**, and click **Save**. Without this, the `packages: write` permission declared in the workflow will not actually be granted, and the push to `ghcr.io` will fail with a permissions error.

3. **No manual secrets need to be created.** This workflow authenticates to `ghcr.io` using `secrets.GITHUB_TOKEN`, which GitHub automatically provisions for every workflow run — you don't add it under **Settings → Secrets and variables**, and it expires once the run finishes. If your Dockerfile ever needs a personal access token (for example, to `git clone` something), stop and reconsider: see the warning below, since that's usually a sign the image is about to include something it shouldn't.

4. **After the image is published for the first time, check its visibility.** Packages pushed to GHCR via `GITHUB_TOKEN` are created **private by default**, even when the source repository is public. Go to the package page (**your organization → Packages → the image name → Package settings**) and change visibility to **Public** if you want others to `docker pull` it without first running `docker login`. This only needs to be done once, after the very first push.

## ⚠️ What the image is allowed to contain

Once published, this image is a **public GHCR package**: anyone can pull it, and anyone can inspect every layer of it, including files that were added and later deleted in a subsequent layer (deleting a file in a later `RUN`/`COPY` step does **not** remove it from the image's history — it's still recoverable from the earlier layer). Because of this, treat anything that ends up in an image layer as if it were posted publicly, and make sure the `Dockerfile` and its build context only reference:

- **Publicly available base images, packages, and libraries** (e.g. official Ubuntu/ROS images, `apt`/`pip`/`apt-get` packages from public repositories, public GitHub repositories cloned over HTTPS with no embedded token).
- **No development code from private lab repositories.** Do not `COPY` source files, scripts, or configuration from `Adorno-Lab` private repositories into the image.
- **No confidential files of any kind** — this includes, but is not limited to: SSH keys, personal access tokens, `.netrc` files, robot network configuration (IP addresses, domain IDs), calibration data, or credentials of any kind, whether copied directly or baked in via build args.
- **No secrets passed as Docker build args.** Build args are visible in the image history (`docker history`) even if not used in the final layer; never pass tokens or credentials this way.

If your image genuinely needs something from a private repository to build, that dependency does not belong in this workflow — talk to the project lead (or with the person responsible for the software architecture in RAICo) about restructuring the build (e.g. publishing the needed component separately, or building privately instead of via this public pipeline).

## Create a runner on GitHub Actions

### Example

```yml
name: Create and publish a Docker image to ghcr.io

on:
  push:
    branches: ['main']
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: adorno-lab/your_base_image_name  # Keep the adorno-lab namespace.
  BUILDX_NO_DEFAULT_ATTESTATIONS: 1 # https://github.com/orgs/community/discussions/45969
  DOCKERFILE_CONTEXT: "."
  DOCKERFILE_PATH: "path_to_your_image/Dockerfile"  
  DOCKERFILE_NAME: "Dockerfile"
  DOCKERFILE_TAG: "latest"

jobs:
  compute-date:
    runs-on: ubuntu-24.04
    outputs:
      date_tag: ${{ steps.date.outputs.date_tag }}
    steps:
      - name: Compute DD_MM_YYYY_HH_MM_SS tag (UTC, runner clock)
        id: date
        run: echo "date_tag=$(date +'%d_%m_%Y_%H_%M_%S')" >> "$GITHUB_OUTPUT"

  build-and-push-image:
    needs: [compute-date]
    strategy:
      fail-fast: false
      matrix:
        arch: [amd64]
        # To also build for arm64, use the line below instead:
        # arch: [amd64, arm64]
    # ubuntu-24.04-arm is GitHub's hosted Arm64 runner label; nothing else here
    # needs to change when arm64 is added to the matrix above.
    runs-on: ${{ matrix.arch == 'amd64' && 'ubuntu-24.04' || 'ubuntu-24.04-arm' }}
    env:
      DATE_TAG: ${{ needs.compute-date.outputs.date_tag }}
    permissions:
      contents: read
      packages: write
      attestations: write
      id-token: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to the Container registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push Docker images
        id: push_image
        uses: docker/build-push-action@v6
        with:
          context: ${{ env.DOCKERFILE_CONTEXT }}
          file: ${{ env.DOCKERFILE_PATH }}
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DOCKERFILE_TAG }}_${{ matrix.arch }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DATE_TAG }}_${{ matrix.arch }}

  # Based on https://github.com/juanjqo/dockerman/blob/main/.github/workflows/docker-image.yml
  create-and-push-manifest:
      runs-on: ubuntu-latest
      permissions:
        contents: read
        packages: write
        attestations: write
        id-token: write
      needs: [compute-date, build-and-push-image]
      env:
        DATE_TAG: ${{ needs.compute-date.outputs.date_tag }}
      steps:
        - name: Set up Docker CLI
          uses: docker/setup-buildx-action@v3
          with:
            install: true

        - name: Log in to the container registry
          uses: docker/login-action@v3
          with:
            registry: ${{ env.REGISTRY }}
            username: ${{ github.actor }}
            password: ${{ secrets.GITHUB_TOKEN }}

        - name: Create and push manifest for ${{ env.DOCKERFILE_TAG }}
          run: |
            docker manifest create ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DOCKERFILE_TAG }} \
              --amend ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DOCKERFILE_TAG }}_amd64 #\
              # --amend ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DOCKERFILE_TAG }}_arm64

            docker manifest push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DOCKERFILE_TAG }}

        - name: Create and push manifest for ${{ env.DATE_TAG }}
          run: |
            docker manifest create ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DATE_TAG }} \
              --amend ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DATE_TAG }}_amd64 #\
              # --amend ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DATE_TAG }}_arm64

            docker manifest push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.DATE_TAG }}
```

## Using the published base image

Once the workflow above has run at least once (and the package's visibility has been set per step 4 of the Prerequisites), the image is available on GHCR.

### Latest version

```shell
docker pull ghcr.io/adorno-lab/sas_unitree_g1_jazzy:latest
```

### Specific version

Every successful run also tags the image with a timestamp in the format `DD_MM_YYYY_HH_MM_SS` (UTC, taken from the runner's clock). Use this to pin to an exact, reproducible build instead of always tracking `latest`:

```shell
docker pull ghcr.io/adorno-lab/sas_unitree_g1_jazzy:18_09_2026_13_54_01
```

You can find all available timestamped tags under the package's page on GitHub (**your organization → Packages → the image name → Tags**).

### In Docker Compose

```yaml
services:
  sas_unitree_g1_jazzy:
    # Pin to a specific published version by its timestamped tag.
    image: ghcr.io/adorno-lab/sas_unitree_g1_jazzy:18_09_2026_13_54_01
```

If the package is still private (or you're pulling from a private one intentionally), authenticate first with `docker login ghcr.io -u <your-github-username>` using a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) that has at least `read:packages` scope.
