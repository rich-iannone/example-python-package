# NOTE: The comments in this file are far more extensive than in a real test suite; they're here
# because this is an educational repository. See tests/README.md for a guided reading order.

# Tests for tinytab/_table.py.

import pytest
from syrupy.extensions.single_file import SingleFileSnapshotExtension, WriteMode

from tinytab import Table, fmt_currency, fmt_number

# ------------------------------------------------------------------------------------------------
# Basics
# ------------------------------------------------------------------------------------------------


def test_table_shape():
    tbl = Table({"item": ["coffee", "bagel"], "price": [3.5, 2.25]})

    assert tbl.columns == ["item", "price"]
    assert tbl.n_rows == 2
    assert repr(tbl) == "<Table: 2 rows x 2 columns>"


def test_table_unequal_columns():
    with pytest.raises(ValueError, match="same length"):
        Table({"a": [1, 2], "b": [1]})


def test_table_fmt_unknown_column():
    tbl = Table({"a": [1, 2]})

    with pytest.raises(KeyError, match="no_such_col"):
        tbl.fmt("no_such_col", str)


# ------------------------------------------------------------------------------------------------
# Fixtures: shared setup
# ------------------------------------------------------------------------------------------------
#
# Many tests need the same starting point, like a table to work with. Rather than build it in
# every test, write a *fixture*: a function, marked with `@pytest.fixture`, that creates the
# thing. A test asks for it by adding a parameter with the fixture's name, and pytest calls the
# fixture and passes in the result.
#
# Each test gets a fresh result (fixtures run once per test by default), so a test that modifies
# its table can't affect any other test.
#
# Fixtures can be found in three places:
#
# - in the same test file (like `formatted_menu` below)
# - in `conftest.py`, which pytest loads automatically; its fixtures are available to every test
#   in that folder and below, without importing anything (like `menu`)
# - built into pytest or plugins (like `tmp_path`, or `snapshot` from syrupy; both used below)
#
# Try it:
#
#   pytest --fixtures                  # list every fixture available, with its docstring


# `menu` comes from conftest.py. Open that file to see how it's defined.
def test_menu_shape(menu):
    assert menu.columns == ["item", "price", "sold"]
    assert menu.n_rows == 3


def test_fmt_returns_new_table(menu):
    formatted = menu.fmt("price", fmt_currency)

    assert formatted is not menu
    assert "$3.50" in formatted.as_text()
    assert "$3.50" not in menu.as_text()


def test_repr_html_matches_as_html(menu):
    # Notebooks call `_repr_html_()` to display an object
    assert menu._repr_html_() == menu.as_html()


# A fixture can use other fixtures, in exactly the same way a test does: by naming them as
# parameters. This one builds on `menu`. Since only this file needs it, it's defined here rather
# than in conftest.py.
@pytest.fixture
def formatted_menu(menu):
    return menu.fmt("price", fmt_currency)


def test_missing_values_render_blank(formatted_menu):
    last_line = formatted_menu.as_text().splitlines()[-1]

    assert last_line.startswith("| croissant")
    assert last_line.rstrip(" |").endswith("$4.00")


# ------------------------------------------------------------------------------------------------
# Built-in fixtures: tmp_path
# ------------------------------------------------------------------------------------------------
#
# pytest comes with fixtures for common needs. `tmp_path` is a `pathlib.Path` to a new, empty
# temporary folder, unique to each test. Tests that write files should always use it: nothing
# gets written into the project, and tests can't trip over each other's files. pytest cleans up
# old temporary folders by itself.
#
# Other useful built-ins: `monkeypatch` (temporarily change environment variables, attributes,
# or dict entries) and `capsys` (capture what was printed).


# Tests can mix fixtures freely: here a built-in one and one of ours.
def test_csv_round_trip(tmp_path, menu):
    path = tmp_path / "menu.csv"

    menu.to_csv(path)
    result = Table.from_csv(path)

    assert path.exists()
    assert result.columns == menu.columns
    assert result.n_rows == menu.n_rows


def test_from_csv_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("a,b\n")

    with pytest.raises(ValueError, match="No data rows"):
        Table.from_csv(path)


# ------------------------------------------------------------------------------------------------
# Fixtures with setup *and* teardown
# ------------------------------------------------------------------------------------------------
#
# When a fixture needs to clean up after the test, use `yield` instead of `return`. Code before
# the `yield` runs before the test, and code after it runs once the test has finished, even if
# the test failed. (A typical use is closing a database connection.)


@pytest.fixture
def csv_file(tmp_path, menu):
    path = tmp_path / "menu.csv"
    menu.to_csv(path)

    yield path

    # Teardown. `tmp_path` would clean this up anyway; it's here to show where teardown goes.
    path.unlink()


def test_from_csv_reads_values_as_strings(csv_file):
    result = Table.from_csv(csv_file)

    assert result.as_text().splitlines()[2] == "| coffee    | 3.5   | 120  |"


# ------------------------------------------------------------------------------------------------
# Skipping tests
# ------------------------------------------------------------------------------------------------
#
# Some tests can only run in some environments. Skipped tests are reported as "skipped" with a
# reason (`-ra` in pyproject.toml lists them in the summary at the end), so they're not lost.
#
# - `@pytest.mark.skipif(condition, reason=...)` skips based on a condition, such as the
#   operating system (`sys.platform == "win32"`) or Python version.
# - `pytest.importorskip("name")` imports a package, or skips the test if it isn't installed.
#   It's the usual way to test support for optional dependencies.
#
# pandas isn't one of tinytab's dependencies (not even in the `dev` extra), so this test is
# usually skipped. Run `pip install pandas` and it runs.


def test_table_accepts_pandas_series():
    pd = pytest.importorskip("pandas")

    tbl = Table({"x": pd.Series([1.5, 2.5])})

    assert tbl.n_rows == 2


# ------------------------------------------------------------------------------------------------
# Snapshot testing
# ------------------------------------------------------------------------------------------------
#
# Some output is too long to write out by hand in a test: a rendered table, an HTML report, a
# chart's SVG. A snapshot test records the output once, saves it to a file, and from then on
# checks that the output still matches that saved copy.
#
# The `snapshot` fixture comes from the syrupy plugin (installed with the `dev` extra).
#
# The workflow:
#
# 1. Write a test that compares against `snapshot`. Running it fails at first, because there's
#    no recorded output yet.
# 2. Run `pytest --snapshot-update` (or `make test-update`) to record it. Snapshots are saved in
#    tests/__snapshots__/, in a file named after the test file (here, `test_table.ambr`). Open
#    it and check that the output is right: from now on, it's what the test expects.
# 3. Commit the snapshot file along with the test.
# 4. Later, if the output changes, the test fails and shows a diff. If the change was a bug,
#    fix the code. If it was intended, run `make test-update` again.
#
# Snapshot changes then show up in `git diff` and in pull requests, so reviewers see exactly how
# the rendered output changed. That review step is the point: a snapshot only proves the output
# didn't change, not that it's correct, so look at each one when you record it.


# The test is a single line, however long the output is.
def test_as_text_snapshot(snapshot, menu):
    assert menu.as_text() == snapshot


def test_as_text_formatted_snapshot(snapshot, menu):
    tbl = menu.fmt("price", fmt_currency).fmt("sold", lambda x: fmt_number(x, decimals=0))

    assert tbl.as_text() == snapshot


# A snapshot is also an easy way to review tricky details, like HTML escaping.
def test_as_html_escapes(snapshot):
    tbl = Table({"name": ["<b>bold</b>", "Tom & Jerry"]})

    assert tbl.as_html() == snapshot


# By default, all the snapshots from one test file go into a single `.ambr` file. A syrupy
# "extension" can store them differently. This one writes each snapshot to its own `.html` file
# (in tests/__snapshots__/test_table/), which you can open in a browser to see the rendered
# result.
class HTMLSnapshotExtension(SingleFileSnapshotExtension):
    file_extension = "html"
    _write_mode = WriteMode.TEXT


# A small fixture wrapping the built-in `snapshot` fixture, so tests can ask for the HTML version.
@pytest.fixture
def snapshot_html(snapshot):
    return snapshot.use_extension(HTMLSnapshotExtension)


def test_as_html_snapshot(snapshot_html, menu):
    assert menu.fmt("price", fmt_currency).as_html() == snapshot_html
