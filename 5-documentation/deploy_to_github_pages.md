# Deploy the documentation to GitHub Pages

This guide sets up a repository so that its Doxygen documentation is published at `https://adorno-lab.github.io/<repository_name>/` and updated automatically on every merge to `main`. It takes about 15 minutes.

The files below are the ones used in [`unitree_drivers`](https://github.com/Adorno-Lab/unitree_drivers). Copy them into your repository and adapt only the parts marked in each step.

> [!NOTE]
> You need **admin** access to the repository for [step 5](#5-enable-github-pages). If you don't have it, ask the project lead to do that step.

## Overview

| Event | What the workflow does |
|-------|------------------------|
| Pull request | Builds the documentation. **Fails if Doxygen reports any warning.** Nothing is published. |
| Push (merge) to `main` | Builds the documentation and publishes it to GitHub Pages |
| Manual run (Actions → Doxygen GitHub Pages → Run workflow) | Same as a push to `main` |

## 1. Install Doxygen locally

You need Doxygen to check the documentation before opening a pull request.

```shell
sudo apt install doxygen
```

> [!TIP]
> The Ubuntu package may be older than the version used by the workflow (`1.18.0`). That is fine for checking your comments; if the CI reports a warning that you don't see locally, install the same version as the CI from the [Doxygen downloads page](https://www.doxygen.nl/download.html).

## 2. Add the `Doxyfile`

Create a file named `Doxyfile` in the repository root. It only lists the settings that differ from Doxygen's defaults; every other setting keeps its default value.

```
# Doxygen configuration for the project documentation website.
#
# Only the settings that differ from Doxygen's defaults are listed here; any
# tag not set falls back to its default. Run `doxygen -x Doxyfile` to see the
# full effective configuration.
#
# Build locally with:   doxygen
# Output:               build/docs/index.html
#
# The GitHub Actions workflow in .github/workflows/doxygen-pages.yml runs the
# same command and publishes build/docs to GitHub Pages.

#---------------------------------------------------------------------------
# Project
#---------------------------------------------------------------------------
PROJECT_NAME           = "<repository_name>"
PROJECT_BRIEF          = "<one-line description of the repository>"
OUTPUT_DIRECTORY       = build
HTML_OUTPUT            = docs

#---------------------------------------------------------------------------
# Input
#---------------------------------------------------------------------------
INPUT                  = README.md include src
RECURSIVE              = YES
FILE_PATTERNS          = *.h *.hpp *.cpp *.md
USE_MDFILE_AS_MAINPAGE = README.md
STRIP_FROM_PATH        = .
STRIP_FROM_INC_PATH    = include

#---------------------------------------------------------------------------
# Extraction
#---------------------------------------------------------------------------
EXTRACT_ALL            = YES
EXTRACT_PRIVATE        = NO
EXTRACT_STATIC         = YES

#---------------------------------------------------------------------------
# Output
#---------------------------------------------------------------------------
GENERATE_HTML          = YES
GENERATE_LATEX         = NO
GENERATE_TREEVIEW      = YES
SOURCE_BROWSER         = YES

#---------------------------------------------------------------------------
# Warnings
#---------------------------------------------------------------------------
QUIET                  = YES
WARN_IF_UNDOCUMENTED   = NO
```

Adapt these settings to your repository:

| Setting | Change it to |
|---------|--------------|
| `PROJECT_NAME` | The repository name |
| `PROJECT_BRIEF` | A one-line description (shown under the name on every page) |
| `INPUT` | `README.md` followed by the folders that contain your code. Only list folders that exist. |
| `FILE_PATTERNS` | Add `*.py` if the repository has Python code to document |
| `STRIP_FROM_INC_PATH` | The folder your headers are included from (e.g. `include`), so pages show `#include <my_package/MyClass.h>` |

Optional settings, added only when needed:

| Setting | Use it when | Example |
|---------|-------------|---------|
| `IMAGE_PATH` | The README or the comments show images stored in the repository | `IMAGE_PATH = design` |
| `EXCLUDE_SYMBOLS` | Some classes are implementation details that should not appear in the documentation (e.g. pImpl classes) | `EXCLUDE_SYMBOLS = *::Impl` |

> [!IMPORTANT]
> The output goes to `build/docs`. Do **not** commit it. Add `build/` to the repository's `.gitignore`:
>
> ```shell
> echo "build/" >> .gitignore
> ```

## 3. Build and check the documentation locally

From the repository root:

```shell
doxygen
```

Open `build/docs/index.html` in a browser:

```shell
xdg-open build/docs/index.html
```

Check that:

- The home page shows your `README.md`.
- **Classes → Class List** shows all your public classes.
- The pages of the classes you documented render correctly. See [Common Pitfalls](README.md#common-pitfalls); some mistakes don't produce any warning.

To reproduce the check that pull requests run (warnings treated as errors):

```shell
( cat Doxyfile; echo "WARN_AS_ERROR = FAIL_ON_WARNINGS" ) | doxygen -
```

Fix every warning it prints. Each one includes the file and line number.

## 4. Add the workflow

Create `.github/workflows/doxygen-pages.yml` with the following content. You do not need to change anything in it.

```yaml
# Builds the Doxygen documentation and publishes it to GitHub Pages.
#
# - Pull requests: build only (Doxygen warnings fail the job), nothing is deployed.
# - Pushes to main / manual runs: build and deploy to GitHub Pages.
#
# One-time repository setup: Settings -> Pages -> Build and deployment ->
# Source: "GitHub Actions".
#
# The site's content is configured in the Doxyfile at the repository root.
name: Doxygen GitHub Pages

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: pages-${{ github.ref }}
  # Never cancel a deployment in progress; superseded PR builds can be cancelled.
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

env:
  DOXYGEN_VERSION: 1.18.0

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Install Doxygen ${{ env.DOXYGEN_VERSION }}
        run: |
          curl -sSL "https://www.doxygen.nl/files/doxygen-${DOXYGEN_VERSION}.linux.bin.tar.gz" | tar -xz
          echo "$PWD/doxygen-${DOXYGEN_VERSION}/bin" >> "$GITHUB_PATH"

      - name: Build documentation
        # Same Doxyfile as local builds, but warnings are treated as errors.
        run: ( cat Doxyfile; echo "WARN_AS_ERROR = FAIL_ON_WARNINGS" ) | doxygen -

      - name: Upload Pages artifact
        if: github.event_name != 'pull_request'
        uses: actions/upload-pages-artifact@v5
        with:
          path: build/docs

  deploy:
    if: github.event_name != 'pull_request'
    needs: build
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v5
```

What it does:

- **`build` job** — downloads the pinned Doxygen version, builds the site with your `Doxyfile` (warnings fail the job), and, except on pull requests, uploads `build/docs` as the Pages artifact.
- **`deploy` job** — publishes the artifact to GitHub Pages. It only runs on pushes to `main` and manual runs.
- **`concurrency`** — a new push to a pull request cancels its previous, now outdated, build. A deployment to Pages is never cancelled halfway.

## 5. Enable GitHub Pages

Do this **once**, **before** merging the workflow to `main`; otherwise the first deployment fails.

1. Open the repository on GitHub → **Settings** → **Pages**.
2. Under **Build and deployment** → **Source**, select **GitHub Actions**.

There is nothing else to configure: no branch to select and no `gh-pages` branch to create.

## 6. Add a documentation badge to the README

Add this badge next to the other badges at the top of `README.md`, replacing `<repository_name>`:

```markdown
[![Docs](https://img.shields.io/badge/docs-GitHub_Pages-green)](https://adorno-lab.github.io/<repository_name>/)
```

## 7. Open a pull request and merge

1. Commit the `Doxyfile`, `.gitignore`, the workflow, and the README change on a new branch, and open a pull request.
2. The **Doxygen GitHub Pages** check runs on the pull request. It must pass before merging.
3. After merging, open the **Actions** tab and wait for the run on `main` to finish. The `deploy` job shows the link to the site.
4. Open `https://adorno-lab.github.io/<repository_name>/` and check it as in [step 3](#3-build-and-check-the-documentation-locally).

From now on, every merge to `main` updates the site.

## Updating the Doxygen version

The version is pinned so that every build of a repository uses the same Doxygen. To upgrade it, change `DOXYGEN_VERSION` in the workflow to a version listed on the [Doxygen downloads page](https://www.doxygen.nl/download.html), and open a pull request: if the new version reports new warnings, the pull request check shows them before anything is published.

Because each repository contains its own workflow, upgrade each repository separately.

## Troubleshooting

| Problem | Cause and fix |
|---------|---------------|
| The `deploy` job fails with a `404` error and asks you to make sure GitHub Pages is enabled | Pages is not enabled for the repository. Do [step 5](#5-enable-github-pages) and re-run the workflow (Actions → the failed run → **Re-run jobs**). |
| `Branch "<name>" is not allowed to deploy to github-pages due to environment protection rules` | The workflow was changed to deploy from a branch other than `main`. Deploy only from `main`; check the result of other branches locally (step 3). |
| The pull request check fails at **Build documentation** | Doxygen reported a warning. Open the failed job; the log shows the file, the line, and the reason. Fix it and push again. |
| The site still shows old content | Check that the latest run on `main` finished successfully in the **Actions** tab, then reload the page without the cache (`Ctrl+Shift+R`). |
| A page shows a **Note** or **Warning** box containing only a fragment of text, or a sentence is cut | A section command is used in the middle of a sentence. See [Common Pitfalls](README.md#common-pitfalls). |
| **Settings → Pages** is not available, or says Pages requires an upgrade | The repository is private and the organization's plan does not include Pages for private repositories. Ask the project lead. |

> [!CAUTION]
> A GitHub Pages site is **public** even when the repository is private (unless the organization uses GitHub Enterprise Cloud with private Pages). Do not enable Pages on a private repository whose code or comments must not be public.

## Checklist

- [ ] `Doxyfile` in the repository root, with `PROJECT_NAME`, `PROJECT_BRIEF`, and `INPUT` adapted
- [ ] `build/` in `.gitignore`
- [ ] Local build with warnings as errors passes (step 3)
- [ ] `.github/workflows/doxygen-pages.yml` added unchanged
- [ ] Settings → Pages → Source set to **GitHub Actions**
- [ ] Documentation badge added to `README.md`
- [ ] Site is live at `https://adorno-lab.github.io/<repository_name>/` and its pages render correctly
