# Documentation

Every Adorno Lab repository must provide Doxygen documentation for its code (see [Mandatory Artifacts](../2-software-design-for-experiments/README.md#51-mandatory-artifacts)). For all **public** repositories, the documentation is published as a website on GitHub Pages and rebuilt automatically by GitHub Actions on every merge to `main`.

Example: [`unitree_drivers`](https://github.com/Adorno-Lab/unitree_drivers), published at [adorno-lab.github.io/unitree_drivers](https://adorno-lab.github.io/unitree_drivers/).



## Core Principles

1. **Documentation lives with the code** — The API reference comes from Doxygen comments in the headers and sources, and the repository's `README.md` is the home page of the site. There is no separate documentation to keep in sync.
2. **Published automatically** — Nobody builds or uploads the site by hand. Merging to `main` updates it.
3. **Self-contained repositories** — Each repository contains its **own** `Doxyfile` and workflow. There is no shared or central workflow, so a repository can be built, read, and changed without looking anywhere else.
4. **Warnings are errors** — Pull requests build the documentation and fail if Doxygen reports any warning, so broken documentation never reaches `main`.


## Tools

| Tool | Role |
|------|------|
| [Doxygen](https://www.doxygen.nl/) (pinned version, currently `1.18.0`) | Generates the HTML site from the code comments and Markdown files |
| [GitHub Actions](https://docs.github.com/en/actions) | Builds the site on pull requests and deploys it on merges to `main` |
| [GitHub Pages](https://docs.github.com/en/pages) | Hosts the site at `https://adorno-lab.github.io/<repository_name>/` |


## Quick Start

A repository needs three files and one setting:

| What | Where | Purpose |
|------|-------|---------|
| `Doxyfile` | Repository root | What to document and how |
| `doxygen-pages.yml` | `.github/workflows/` | Builds and deploys the site |
| `build/` entry | `.gitignore` | Keeps the generated HTML out of Git |
| Pages source: **GitHub Actions** | Settings → Pages | Allows the workflow to publish (one time) |

Follow [Deploy the documentation to GitHub Pages](deploy_to_github_pages.md) for the files to copy and the step-by-step setup.


## Writing Documentation Comments

Document the public API in the headers with `/** ... */` blocks placed **immediately before** the declaration they describe:

```cpp
/**
 * @brief Sets the target joint positions of @p limb, in radians.
 * @param limb Which joint group to set.
 * @param target_positions Exactly get_num_joints(limb) positions.
 * @throws std::invalid_argument if the size does not match get_num_joints(limb).
 * @note Until this is called for a limb, that limb holds its measured pose.
 */
void set_target_positions(const LIMB& limb, const std::vector<double>& target_positions);
```

### Common Pitfalls

> [!WARNING]
> Doxygen does **not** report the first two pitfalls below. The build passes, but the page renders incorrectly. Always look at the generated page of the classes you documented.

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| A section command in the middle of a sentence: `(see the class-level @warning).` | `@warning` starts a new section, so the sentence is cut and an extra **Warning** box appears containing only `).` | Write the word without `@`: `(see the class-level warning).` The same applies to `@note`, `@details`, `@return`, `@param`, etc. |
| The same reference at the start of a wrapped line: `* @warning above before using this value.` | Same as above | Rewrap the line or remove the `@` |
| A doc comment that is not directly above its declaration (e.g. two `/** */` blocks in a row) | The comment is attached to the wrong function | Move each comment right above its own declaration |
| `/*` inside a comment, e.g. `see example/low_level/*.cpp` | Doxygen sees a nested comment and misreads the rest of the file: `warning: Reached end of file while still inside a (nested) comment` | Escape it as `\*.cpp` or rephrase |
| `@param` with a name that is not in the signature | `warning: argument 'x' of command @param is not found in the argument list` | Use the exact parameter names |

Inline commands such as `@p name`, `@c code`, and `@ref` are fine in the middle of a sentence; only section commands (`@brief`, `@details`, `@note`, `@warning`, `@param`, `@return`, `@throws`, ...) cause the problem above.
