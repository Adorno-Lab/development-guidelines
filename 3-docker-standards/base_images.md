# Creating base images

Base images are added to [`Adorno-Lab/raico_base_images`](https://github.com/Adorno-Lab/raico_base_images), which contains the layout, the publishing workflow, and how to open a PR for a new one — see that repo's `CONTRIBUTING.md` and its `.github/workflow-templates/build-and-publish.yml`. Don't set this up in your own project's repository, and don't copy a workflow from here — it won't stay in sync with that repo's actual layout.

What follows is lab policy that applies regardless of which image or repo you're touching.

## ⚠️ What the image is allowed to contain

Once published, a base image is a **public GHCR package**: anyone can pull it, and anyone can inspect every layer of it, including files that were added and later deleted in a subsequent layer (deleting a file in a later `RUN`/`COPY` step does **not** remove it from the image's history — it's still recoverable from the earlier layer). Because of this, treat anything that ends up in an image layer as if it were posted publicly, and make sure the `Dockerfile` and its build context only reference:

- **Publicly available base images, packages, and libraries** (e.g. official Ubuntu/ROS images, `apt`/`pip`/`apt-get` packages from public repositories, public GitHub repositories cloned over HTTPS with no embedded token).
- **No development code from private lab repositories.** Do not `COPY` source files, scripts, or configuration from `Adorno-Lab` private repositories into the image.
- **No confidential files of any kind** — this includes, but is not limited to: SSH keys, personal access tokens, `.netrc` files, robot network configuration (IP addresses, domain IDs), calibration data, or credentials of any kind, whether copied directly or baked in via build args.
- **No secrets passed as Docker build args.** Build args are visible in the image history (`docker history`) even if not used in the final layer; never pass tokens or credentials this way.
- **No manual secrets are needed to publish.** The workflow authenticates to `ghcr.io` using `secrets.GITHUB_TOKEN`, which GitHub provisions automatically. If your Dockerfile ever seems to need a personal access token (for example, to `git clone` something private), that's usually a sign the image is about to include something it shouldn't — stop and talk to the project lead instead.

If your image genuinely needs something from a private repository to build, that dependency does not belong in this pipeline — talk to the project lead (or with the person responsible for the software architecture in RAICo) about restructuring the build (e.g. publishing the needed component separately, or building privately instead of via this public pipeline).

## Package visibility

Packages pushed to GHCR via `GITHUB_TOKEN` are created **private by default**, even from a public repository. After an image is published for the first time, its visibility needs to be checked and, if needed, changed once: **your organization → Packages → the image name → Package settings → Public**. This step could require permissions you don't have on the repository — in that case, ask the project lead to do it for you.

> [!CAUTION]
> **DO NOT CHANGE THE VISIBILITY OF A PACKAGE UNDER ANY CIRCUMSTANCE WITHOUT THE AUTHORIZATION OF THE PROJECT LEAD.**

For how to pull a published image and pin to a specific version, see [Versioning and Pinning](README.md#versioning-and-pinning) in the main Docker standards doc.

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
