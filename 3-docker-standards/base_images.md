

## Prerequisites

## Create a runner on Github actions


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
