# Documentation for private repositories

> [!IMPORTANT]
> Private repositories **must not** publish anything on GitHub Pages. A Pages site is public even when the repository is private, so it would expose the code and its comments.
>
> Instead, a private repository **must**:
> - include the generated documentation in a `docs/` folder at the repository root, and
> - explain in its `README.md` how to open and regenerate it.

This guide sets that up. It uses the same Doxygen configuration as public repositories ([Deploy the documentation to GitHub Pages](deploy_to_github_pages.md)), except that the output goes to `docs/` and is committed, and there is no workflow.

## Overview

| | Public repositories | Private repositories |
|---|---|---|
| Generated documentation | Built by GitHub Actions, published on GitHub Pages | Built locally, committed in `docs/` |
| `.github/workflows/doxygen-pages.yml` | Required | **Must not** be added |
| Settings → Pages | Source: **GitHub Actions** | **Disabled** |
| Readers open the documentation at | `https://adorno-lab.github.io/<repository_name>/` | `docs/index.html` in their clone |
| Warnings checked by | The pull request check | The author, locally, before committing |

## 1. Install the pinned Doxygen version

Use the **same Doxygen version as public repositories (`1.18.0`)**, not the Ubuntu package. The generated HTML depends on the Doxygen version: regenerating `docs/` with a different version changes almost every file, which buries the real changes in the pull request diff.

Install it in your custom prefix (see [this guide](https://ros2-tutorial.readthedocs.io/en/latest/cmake/cmake_packages_without_sudo.html) for background); no sudo is needed:

```shell
mkdir -p ~/opt
curl -sSL https://www.doxygen.nl/files/doxygen-1.18.0.linux.bin.tar.gz | tar -xz -C ~/opt
```

Check it:

```shell
~/opt/doxygen-1.18.0/bin/doxygen --version
```

> [!TIP]
> To call it simply as `doxygen`, add `export PATH=$HOME/opt/doxygen-1.18.0/bin:$PATH` to your `~/.bashrc`. The commands below use the full path so that they work either way.

## 2. Add the `Doxyfile`

Create a file named `Doxyfile` in the repository root:

```
# Doxygen configuration for the project documentation.
#
# Only the settings that differ from Doxygen's defaults are listed here; any
# tag not set falls back to its default. Run `doxygen -x Doxyfile` to see the
# full effective configuration.
#
# This is a private repository: the documentation is NOT published on GitHub
# Pages. It is generated locally into docs/ and committed. To regenerate it
# (Doxygen 1.18.0):
#
#   rm -rf docs
#   doxygen
#
# Output:               docs/index.html

#---------------------------------------------------------------------------
# Project
#---------------------------------------------------------------------------
PROJECT_NAME           = "<repository_name>"
PROJECT_BRIEF          = "<one-line description of the repository>"
OUTPUT_DIRECTORY       = .
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

Adapt `PROJECT_NAME`, `PROJECT_BRIEF`, `INPUT`, `FILE_PATTERNS`, and `STRIP_FROM_INC_PATH`, and add the optional settings if needed, exactly as for public repositories (see the tables in [step 2 of the public guide](deploy_to_github_pages.md#2-add-the-doxyfile)).

> [!WARNING]
> Do not change `OUTPUT_DIRECTORY` or `HTML_OUTPUT`, and keep `docs/` for the generated documentation **only**. Regenerating starts with `rm -rf docs`, which deletes everything in that folder.

## 3. Mark `docs/` as generated

Create a `.gitattributes` file in the repository root (or add the line to the existing one):

```shell
echo "docs/** linguist-generated=true" >> .gitattributes
```

GitHub then collapses the changes in `docs/` in pull request diffs, so reviewers see the code changes first, and leaves `docs/` out of the repository's language statistics.

Make sure `docs/` is **not** listed in `.gitignore`.

## 4. Generate and check the documentation

From the repository root:

```shell
rm -rf docs
~/opt/doxygen-1.18.0/bin/doxygen
```

`rm -rf docs` removes pages of classes or files that no longer exist; Doxygen does not delete them on its own.

Then check it with warnings treated as errors. This is the same check that public repositories run on every pull request; in a private repository, you are responsible for running it:

```shell
( cat Doxyfile; echo "WARN_AS_ERROR = FAIL_ON_WARNINGS" ) | ~/opt/doxygen-1.18.0/bin/doxygen -
```

Fix every warning it prints. Each one includes the file and line number.

Open `docs/index.html` and check it as described in [step 3 of the public guide](deploy_to_github_pages.md#3-build-and-check-the-documentation-locally):

```shell
xdg-open docs/index.html
```

## 5. Add the instructions to the README

Add this section to the repository's `README.md`:

````markdown
## Documentation

The Doxygen documentation of this repository is in the [`docs`](docs) folder. GitHub shows HTML files as source code, so clone the repository and open `docs/index.html` in a browser:

```shell
xdg-open docs/index.html
```

### Regenerating the documentation

Regenerate it whenever you change the code or its comments, and commit the result together with your changes. You need [Doxygen 1.18.0](https://www.doxygen.nl/download.html) (see [Documentation for private repositories](https://github.com/Adorno-Lab/development-guidelines/blob/main/5-documentation/docs_for_private_repositories.md#1-install-the-pinned-doxygen-version)). From the repository root:

```shell
rm -rf docs
~/opt/doxygen-1.18.0/bin/doxygen
```

Doxygen must not report any warning. To check, run:

```shell
( cat Doxyfile; echo "WARN_AS_ERROR = FAIL_ON_WARNINGS" ) | ~/opt/doxygen-1.18.0/bin/doxygen -
```
````

## 6. Commit the documentation

Commit the `Doxyfile`, `.gitattributes`, the `docs/` folder, and the README change on a new branch, and open a pull request.

From then on, **every pull request that changes the code or its comments must also include the regenerated `docs/`**. Reviewers should check that it does.

## Changing the repository's visibility

| Change | What to do |
|--------|------------|
| Private → public | Delete the `docs/` folder and the `docs/**` line from `.gitattributes`. Set up GitHub Pages following [Deploy the documentation to GitHub Pages](deploy_to_github_pages.md) (use the `Doxyfile` from there, which builds into `build/docs`). Replace the README's **Documentation** section with the docs badge. |
| Public → private | **Before** changing the visibility, unpublish the site (Settings → Pages → **Unpublish site**) and delete `.github/workflows/doxygen-pages.yml`. Then follow this guide from [step 1](#1-install-the-pinned-doxygen-version). |

## Troubleshooting

| Problem | Cause and fix |
|---------|---------------|
| The pull request diff of `docs/` changes almost every file, even for a small code change | `docs/` was generated with a different Doxygen version. Regenerate it with `1.18.0` ([step 1](#1-install-the-pinned-doxygen-version)). |
| `docs/` still contains pages of classes that were removed | It was regenerated without `rm -rf docs` first. Regenerate it as in [step 4](#4-generate-and-check-the-documentation). |
| A page shows a **Note** or **Warning** box containing only a fragment of text, or a sentence is cut | A section command is used in the middle of a sentence. See [Common Pitfalls](README.md#common-pitfalls). |

## Checklist

- [ ] No GitHub Pages site (Settings → Pages is disabled) and no `doxygen-pages.yml` workflow
- [ ] `Doxyfile` in the repository root, with `PROJECT_NAME`, `PROJECT_BRIEF`, and `INPUT` adapted, writing to `docs/`
- [ ] `docs/** linguist-generated=true` in `.gitattributes`, and `docs/` not in `.gitignore`
- [ ] `docs/` generated with Doxygen `1.18.0`, after `rm -rf docs`
- [ ] Check with warnings as errors passes
- [ ] `docs/` committed
- [ ] `README.md` has a **Documentation** section explaining how to open and regenerate `docs/`
