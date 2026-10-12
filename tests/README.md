# tests

> [!NOTE]
> The test files here are far more heavily commented than a real project's tests. That's for
> teaching: in a real test suite, a good test name plus a readable test body usually says
> enough, and comments are kept for the non-obvious (why a tolerance was chosen, which bug a
> test guards against).

## How the tests are organized

Each test file maps to one module in the package:

| Test file | Tests for |
|---|---|
| `test_formats.py` | `tinytab/_formats.py` |
| `test_stats.py` | `tinytab/_stats.py` |
| `test_table.py` | `tinytab/_table.py` |
| `test_package.py` | the package as a whole: `__version__` and the public API in `tinytab/__init__.py` |

The rules:

- **One test file per module**, so the tests for any piece of code are easy to find.
- **A private module's leading underscore is dropped** from the test file name: `_formats.py` is
  tested by `test_formats.py`. The underscore tells users "not public API"; tests don't need it.
- **`test_package.py` is the one exception**: it checks the package as a whole rather than a
  single module.

Also in this folder:

- `conftest.py`: fixtures shared by every test file
- `__snapshots__/`: recorded output for the snapshot tests in `test_table.py`. These files are
  committed to git

The examples in the package's docstrings aren't run by pytest. They're Quarto `{python}` cells,
run whenever the documentation site is built (`make docs`, and in CI), so an example that stops
working fails the docs build. They show how to use the package, and the tests here are what check
that it behaves correctly.

## Reading order

Within each file, the tests go from simple to more advanced, in sections. To learn pytest step
by step, read the sections in this order:

| # | Topic | Where |
|---|---|---|
| 1 | Test discovery, plain `assert`, failure messages, naming tests | `test_formats.py`: *First tests* |
| 2 | Arrange/act/assert; edge cases | `test_stats.py`: *Basics* |
| 3 | One test, many cases: `parametrize`, `ids=`, `pytest.param` | `test_formats.py`: *Parametrize* |
| 4 | Checking errors: `pytest.raises`, `match=`, `excinfo` | `test_formats.py`: *Errors* |
| 5 | Checking warnings: `pytest.warns` | `test_stats.py`: *Errors and warnings* |
| 6 | Comparing floats: `pytest.approx` | `test_stats.py`: *Floats* |
| 7 | Testing result objects | `test_stats.py`: *Result objects* |
| 8 | Fixtures and `conftest.py` | `test_table.py`: *Fixtures*, and `conftest.py` |
| 9 | Built-in fixtures: `tmp_path`; `yield` for teardown | `test_table.py`: *Built-in fixtures*, *Fixtures with setup and teardown* |
| 10 | Markers: custom markers and `-m` | `test_stats.py`: *Markers* |
| 11 | `xfail` for known failures | `test_formats.py`: *xfail* |
| 12 | Skipping: `skipif`, `importorskip` | `test_table.py`: *Skipping tests* |
| 13 | Snapshot testing with syrupy | `test_table.py`: *Snapshot testing* |
| 14 | Testing the package as a whole | `test_package.py` |
