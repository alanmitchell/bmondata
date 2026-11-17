# Building and Publishing `bmondata`

This project uses [uv](https://docs.astral.sh/uv/) for dependency management,
building, and publishing to [PyPI](https://pypi.org/project/bmondata/).

## One-time setup

1. **Install uv** (if not already present):

       curl -LsSf https://astral.sh/uv/install.sh | sh

   Upgrade an existing install with `uv self update`.

2. **Create a PyPI API token.** Log in at <https://pypi.org/manage/account/>,
   go to *API tokens* → *Add API token*, scope it to the `bmondata` project, and
   copy the token (it starts with `pypi-`). It is shown only once.

3. **Store the token** so you don't have to paste it on every upload. Put it in
   your shell profile (`~/.bashrc`) as:

       export UV_PUBLISH_TOKEN="pypi-...."

   Optionally repeat this for TestPyPI with a token from
   <https://test.pypi.org/manage/account/>; see "Trial upload" below.

## Day-to-day development

Create/refresh the local virtual environment in `.venv` from `uv.lock`:

    uv sync

Run anything inside that environment with `uv run`, which syncs first so the
environment is always up to date:

    uv run python
    uv run jupyter lab        # if jupyter has been added as a dev dependency

There is no need to activate the environment manually, though `source
.venv/bin/activate` works if you prefer.

### Changing dependencies

Add or remove runtime dependencies with uv rather than hand-editing
`pyproject.toml`, so that `uv.lock` stays in step:

    uv add "pytz"
    uv remove pytz

Development-only tools go in a dependency group, which is not installed for
users of the published package:

    uv add --dev jupyterlab

Both `pyproject.toml` and `uv.lock` change as a result, and both are committed.

## Updating the version number

The version lives in **exactly one place**: the `__version__` string at the top
of `bmondata/__init__.py`. The build reads it from there (via the
`[tool.hatch.version]` setting in `pyproject.toml`), so `pyproject.toml` has no
version of its own to keep in sync.

To release a new version, edit that one line and add a note to the version
history comment just below it:

```python
__version__ = '1.0.7'
# Version info
# 1.0.7: Short description of what changed in this release.
# 1.0.6: Added handling of building or organization ID of 0
...
```

Notes:

* Use [semantic versioning](https://semver.org/): bump the patch number for
  fixes, the minor number for new backward-compatible features, and the major
  number for breaking changes.
* **A version number can never be reused on PyPI**, even if the release is
  deleted. If an upload turns out to be broken, bump the version and upload
  again rather than trying to replace it.
* Because the version is dynamic, `uv version --bump patch` does *not* work on
  this project; it only edits a static version in `pyproject.toml`. Editing
  `bmondata/__init__.py` is the supported way.

Confirm the version uv will build:

    uv run python -c "import bmondata; print(bmondata.__version__)"

## Building the distributions

From the project root:

    uv build

This writes two files to `dist/`:

* `bmondata-<version>.tar.gz` — the source distribution
* `bmondata-<version>-py3-none-any.whl` — the wheel

`dist/` is git-ignored. **Clear out old builds first** so that a publish does
not also try to re-upload previous releases:

    rm -rf dist
    uv build

Sanity-check what went into the wheel:

    unzip -l dist/bmondata-*.whl

## Trial upload to TestPyPI (optional)

TestPyPI is a throwaway copy of PyPI, useful for checking that the metadata and
README render correctly before a real release:

    uv publish --index testpypi --token "pypi-...<TestPyPI token>..."

Then verify a clean install from it:

    uv run --no-project --with bmondata --index https://test.pypi.org/simple/ \
        python -c "import bmondata; print(bmondata.__version__)"

TestPyPI accounts and tokens are separate from PyPI ones, and TestPyPI versions
are also permanently consumed, so expect to burn a few patch numbers if you
lean on it.

## Uploading to PyPI

First confirm what will be uploaded, without actually sending it:

    uv publish --dry-run

Then publish:

    uv publish

With `UV_PUBLISH_TOKEN` set in the environment this needs no further input.
Otherwise pass the token explicitly:

    uv publish --token "pypi-...."

Confirm the release, waiting a minute or two for the index to update:

    uv run --no-project --with bmondata --no-cache \
        python -c "import bmondata; print(bmondata.__version__)"

and check the project page at <https://pypi.org/project/bmondata/>.

## Full release checklist

1. Make and commit the code changes.
2. Bump `__version__` in `bmondata/__init__.py` and add a version history note.
3. `uv sync` and smoke-test the change.
4. `rm -rf dist && uv build`
5. `uv publish --dry-run`, then `uv publish`
6. Verify the install from PyPI (command above).
7. Commit, tag, and push:

       git commit -am "Version 1.0.7: <summary>"
       git tag v1.0.7
       git push && git push --tags

## Troubleshooting

| Problem | Cause / fix |
| --- | --- |
| `File already exists` on publish | That version is already on PyPI. Bump `__version__`, rebuild, and publish again. |
| `uv publish` uploads an old release too | Stale files in `dist/`. `rm -rf dist && uv build`. |
| `403 Forbidden` on publish | Token is missing, expired, or scoped to a different project. Create a new scoped token. |
| `error: We cannot get or set dynamic project versions` | Expected — `uv version` is not usable here. Edit `bmondata/__init__.py` instead. |
| Build picks up the wrong version | `uv build` reads `bmondata/__init__.py`; make sure the edit was saved. |
