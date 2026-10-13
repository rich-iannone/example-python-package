<div align="center">

# example-python-package

_This is how *I* package, test, and release Python libraries (shown using a small working example)._

[![CI](https://github.com/rich-iannone/example-python-package/actions/workflows/ci.yml/badge.svg)](https://github.com/rich-iannone/example-python-package/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-site-blue)](https://rich-iannone.github.io/example-python-package/)
![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/rich-iannone/example-python-package/blob/main/LICENSE)
![Repo status: example](https://img.shields.io/badge/status-educational%20example-orange)

</div>

## Why do this repo exist anyway?

Advice about Python packaging usually comes in piecemeal fashion. You might see a guide to
`pyproject.toml` in one place, a pytest tutorial there elsewhere, and a nice CI recipe in a
completely different location on the Internet. Each of these bits makes sense on its own, but it's
really kinda hard to see how the pieces fit together in a real project.

This repo provides all of it in one place. It's a small (but complete!) package where the packaging,
tests, type checking, linting, CI, and documentation all work together. Every practice in the
[Python Packaging reference](https://rich-iannone.github.io/example-python-package/packaging/)
can be seen working here.

## It's opinionated by design... my design

These are the conventions I stick to in my Python projects, not the only reasonable ones. There
might be all sorts of good alternatives (e.g., `setuptools` or `hatchling`, a flat or a `src/`
layout, `syrupy` or `pytest-snapshot`, etc.), but, the repo picks one and uses it consistently. The
reference explains the reasoning behind the choices, so you can pick the ones that fit your own
projects.

What seemed to work for me is having consistency, where the choices are made once and applied
everywhere. In this way, I've found that moving between projects became super easy. For example,
`make test` always means the same thing (running the tests).

## How to read it

The package is small on purpose. The `tinytab` library in here is but a morsel of
[Great Tables](https://github.com/posit-dev/great-tables), with a few formatting functions and a way
to make a very simple table. With this sort of setup, I'm able to keep the focus on the package
setup itself (rather than on the code). The repo is like an onion as it can be read in layers:

1. The package, in [`tinytab/`](https://github.com/rich-iannone/example-python-package/tree/main/tinytab):
   a private-module layout with an explicit public API, type hints throughout, and NumPy-style
   docstrings whose examples run when the docs are built.
2. The tests, in [`tests/`](https://github.com/rich-iannone/example-python-package/tree/main/tests):
   one test file per module, covering most of what pytest offers (parametrize, fixtures,
   markers, snapshot tests, and more). The [tests README](https://github.com/rich-iannone/example-python-package/blob/main/tests/README.md)
   gives a reading order for learning pytest step by step.
3. The configs: `pyproject.toml`, the `Makefile`, the pre-commit config, and the CI
   workflows. These are where most of the decisions live.
4. The documentation site, described below.

The files are *way* more heavily commented than a real project's would be, explaining in
excruciating detail what each little thing does and why. This is on purpose so that you'll
eventually learn a lot.

## The documentation site

The [docs site](https://rich-iannone.github.io/example-python-package/) is built with
[Great Docs](https://github.com/posit-dev/great-docs), which turns a package's docstrings and a
collection of .qmd files into a really beautiful documentation site with not too much configuration.
The site is built from the
[`docs/`](https://github.com/rich-iannone/example-python-package/tree/main/docs) folder and
published to GitHub Pages. It has three parts:

- the User Guide: how to use `tinytab`, with code that runs as the site is built
- the Reference section: the API reference, generated from the docstrings, with examples that show
  their real output
- the 'Python Packaging' section: the reference behind this repo, covering project setup, testing,
  CI, code and API design, and documentation

The site is itself one of the examples: it shows what a package's documentation looks like when
it's built with the same care as the code.

## What's here

| File | What it shows |
|---|---|
| [Python Packaging reference](https://rich-iannone.github.io/example-python-package/packaging/) | The practices themselves, written down (part of the docs site) |
| [`docs/`](https://github.com/rich-iannone/example-python-package/tree/main/docs) | The documentation site, built with Great Docs: API reference, user guide, and the packaging reference |
| [`pyproject.toml`](https://github.com/rich-iannone/example-python-package/blob/main/pyproject.toml) | Metadata, extras, and all tool config (pytest, coverage, ruff, pyright) in one place |
| [`Makefile`](https://github.com/rich-iannone/example-python-package/blob/main/Makefile) | The developer interface: `make test`, `make check`, `make docs`, ... |
| [`tests/`](https://github.com/rich-iannone/example-python-package/tree/main/tests) | pytest tests: fixtures, parametrize, error and warning checks, snapshot tests |
| [`playground.qmd`](https://github.com/rich-iannone/example-python-package/blob/main/playground.qmd) | A scratch space for trying the package interactively |
| [`.github/workflows/`](https://github.com/rich-iannone/example-python-package/tree/main/.github/workflows) | CI (lint, type-check, tests across Python 3.10–3.14 on Linux and Windows) and the docs site build |

## The example package called `tinytab`

The `tinytab` package formats values and renders small tables. Here's an example.

```python
from tinytab import Table, fmt_currency

tbl = Table({"item": ["coffee", "bagel"], "price": [3.5, 2.25]})
print(tbl.fmt("price", fmt_currency).as_text())
```

```
| item   | price |
|--------|-------|
| coffee | $3.50 |
| bagel  | $2.25 |
```

## Trying it out

```bash
git clone https://github.com/rich-iannone/example-python-package.git
cd example-python-package
python -m venv .venv
make install       # the package, plus pytest, ruff, pyright, and the other dev tools
make test          # run the tests
make check         # format, lint, type-check, and test: everything CI checks
```

To build the docs site locally, install the docs tools too (this needs
[Quarto](https://quarto.org/) installed):

```bash
make install-docs
make docs-preview
```

Run `make help` to see all the targets.

## License

MIT. See [LICENSE](https://github.com/rich-iannone/example-python-package/blob/main/LICENSE).
