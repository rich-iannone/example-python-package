<div align="center">

# example-python-package

_How I package, test, and ship Python libraries, shown on a small working example._

[![CI](https://github.com/rich-iannone/example-python-package/actions/workflows/ci.yml/badge.svg)](https://github.com/rich-iannone/example-python-package/actions/workflows/ci.yml)
![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Repo status: example](https://img.shields.io/badge/status-educational%20example-orange)

</div>

> [!NOTE]
> **This is educational reference material, not a real library.** The `tinytab` package exists
> only to give the packaging and testing practices something concrete to work on. It isn't (and
> won't ever be) published to PyPI and won't be maintained as a library.

## What's here

| File | What it shows |
|---|---|
| [`PYTHON_PACKAGING_PRACTICES.md`](PYTHON_PACKAGING_PRACTICES.md) | The practices themselves, written down |
| [`DEMO.md`](DEMO.md) | A step-by-step walkthrough of testing with pytest (the run-of-show for a live demo) |
| [`pyproject.toml`](pyproject.toml) | Metadata, extras, and all tool config (pytest, coverage, ruff, pyright) in one place |
| [`Makefile`](Makefile) | The developer interface: `make test`, `make check`, `make build`, ... |
| [`tests/`](tests/) | pytest tests: fixtures, parametrize, error and warning checks, snapshot tests |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | CI: lint and type-check, then tests across Python 3.10–3.14 on Linux and Windows |

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

MIT. See [LICENSE](LICENSE).
