<div align="center">

# example-python-package

_How I package, test, and ship Python libraries, shown on a small working example._

[![CI](https://github.com/rich-iannone/example-python-package/actions/workflows/ci.yml/badge.svg)](https://github.com/rich-iannone/example-python-package/actions/workflows/ci.yml)
![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/rich-iannone/example-python-package/blob/main/LICENSE)
![Repo status: example](https://img.shields.io/badge/status-educational%20example-orange)

</div>

> **Note: this is educational reference material, not a real library.** The `tinytab` package exists
> only to give the packaging and testing practices something concrete to work on. It isn't (and
> won't ever be) published to PyPI and won't be maintained as a library.

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

## The example package

`tinytab` formats values and renders small tables:

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
make install
make test
```

Run `make help` to see the other targets.

## License

MIT. See [LICENSE](https://github.com/rich-iannone/example-python-package/blob/main/LICENSE).
