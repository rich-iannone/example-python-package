# NOTE: The comments in this file are far more extensive than in a real test suite; they're here
# because this is an educational repository. See tests/README.md for a guided reading order.

# Tests for tinytab/_formats.py. Each test file maps to one module in the package, so the tests
# for any piece of code are easy to find. (The module's leading underscore, which marks it as
# private, isn't carried over to the test file's name.)
#
# How pytest finds tests ("test discovery"):
#
# - it looks in the folders listed in `testpaths` (in pyproject.toml)
# - in files named `test_*.py`
# - for functions named `test_*`
#
# That's all. There's no base class to inherit from and nothing to register. A test is a
# function that calls your code and checks the result with a plain `assert`. The test fails if
# an assert fails or if any exception escapes, and passes otherwise.
#
# Try it:
#
#   pytest tests/test_formats.py -v                              # this file, one line per test
#   pytest tests/test_formats.py::test_fmt_number_default        # a single test

import pytest

from tinytab import fmt_currency, fmt_number, fmt_percent

# ------------------------------------------------------------------------------------------------
# First tests: plain assert
# ------------------------------------------------------------------------------------------------


# The simplest possible test: call a function, assert on the result.
#
# When an assert fails, pytest shows you the values on both sides, e.g.
#
#   AssertionError: assert '1234.57' == '1,234.57'
#
# It does this by rewriting `assert` statements in test files as they're imported ("assertion
# rewriting"). That's why plain `assert` is enough, with no `assertEqual()` and friends.
# Try breaking `fmt_number()` to see it.
def test_fmt_number_default():
    assert fmt_number(1234.567) == "1,234.57"


# Test names matter: when a test fails, its name is the first thing you read. Name tests after
# the behavior they check, so the failure report says what broke.
def test_fmt_number_rounds_to_requested_decimals():
    assert fmt_number(1234.567, decimals=0) == "1,235"
    assert fmt_number(1234.567, decimals=1) == "1,234.6"


def test_fmt_currency_defaults_to_usd():
    assert fmt_currency(1234.5) == "$1,234.50"


# ------------------------------------------------------------------------------------------------
# Parametrize: one test function, many cases
# ------------------------------------------------------------------------------------------------
#
# Often you want to check the same behavior with many inputs. You could write a loop inside a
# test, but then the first failing case hides all the others, and the report doesn't say which
# input failed. `@pytest.mark.parametrize` turns each case into its own test instead: each one
# passes or fails on its own and is reported by name.
#
# Try it:
#
#   pytest tests/test_formats.py -v     # see each case listed separately
#   pytest -k jpy                       # only tests whose name or id contains "jpy" (any case)


# The first argument names the parameters (as one comma-separated string); the second is a
# list with one tuple of values per case. pytest calls the test once per tuple, passing the
# values in as arguments with those names.
#
# Without `ids=`, pytest builds test ids from the values: `test_fmt_number_many[1000000-...]`.
@pytest.mark.parametrize(
    "x, expected",
    [
        (0, "0.00"),
        (1, "1.00"),
        (-1, "-1.00"),
        (1_000_000, "1,000,000.00"),
        (1234.5678, "1,234.57"),
    ],
)
def test_fmt_number_many(x, expected):
    assert fmt_number(x) == expected


# When the values don't make readable ids, give each case a name with `ids=`. Failures then read
# like `test_fmt_currency[jpy-no-decimals]`, which says what the case was for.
@pytest.mark.parametrize(
    "x, currency, expected",
    [
        (1234.5, "USD", "$1,234.50"),
        (1234.5, "EUR", "€1,234.50"),
        (1234.5, "eur", "€1,234.50"),
        (1234.5, "JPY", "¥1,234"),
        (-5, "GBP", "-£5.00"),
    ],
    ids=["usd", "eur", "lowercase-code", "jpy-no-decimals", "negative"],
)
def test_fmt_currency(x, currency, expected):
    assert fmt_currency(x, currency=currency) == expected


# With `ids=` in a separate list, it's easy for the ids and the cases to drift out of order.
# `pytest.param()` keeps each case's id right next to its values.
@pytest.mark.parametrize(
    "x, expected",
    [
        pytest.param(0.256, "25.6%", id="typical"),
        pytest.param(1, "100.0%", id="whole"),
        pytest.param(0, "0.0%", id="zero"),
        pytest.param(1.5, "150.0%", id="over-100"),
    ],
)
def test_fmt_percent(x, expected):
    assert fmt_percent(x) == expected


# Stacking parametrize decorators tests every combination: 4 currencies x 2 signs = 8 tests.
# This suits properties that should hold for all inputs, rather than exact expected outputs.
@pytest.mark.parametrize("currency", ["USD", "EUR", "GBP", "JPY"])
@pytest.mark.parametrize("x", [12.5, -12.5])
def test_fmt_currency_sign_comes_first(x, currency):
    result = fmt_currency(x, currency=currency)

    assert result.startswith("-") == (x < 0)


# ------------------------------------------------------------------------------------------------
# Errors: testing that code fails correctly
# ------------------------------------------------------------------------------------------------
#
# How code behaves when given bad input is part of its API, so test it too: that it raises the
# right kind of error, and that the message tells the user what went wrong and how to fix it.


# `pytest.raises` is a context manager: the test passes only if the code inside the `with`
# block raises that exception type (or a subclass). If nothing is raised, the test fails.
#
# `match=` also checks the error message. It's a regular expression, searched for anywhere in
# the message (with `re.search`), so a distinctive fragment is enough.
def test_fmt_currency_unknown_code():
    with pytest.raises(ValueError, match="Unknown currency 'XYZ'"):
        fmt_currency(10, currency="XYZ")


# Because `match=` is a regular expression, characters like `.` `(` and `[` have special
# meanings. Wrap a literal message in `re.escape()` if it contains them. (Backticks are safe,
# so this one is fine as is.)
def test_fmt_number_negative_decimals():
    with pytest.raises(ValueError, match="`decimals` must be zero or greater"):
        fmt_number(1.0, decimals=-1)


# `as excinfo` captures the exception, so you can check it in more detail after the block.
# `excinfo.value` is the exception object itself. Here we check that the message lists the
# currencies that *are* valid, so the user can fix their mistake.
def test_fmt_currency_error_lists_valid_codes():
    with pytest.raises(ValueError) as excinfo:
        fmt_currency(10, currency="XYZ")

    message = str(excinfo.value)
    for code in ["USD", "EUR", "GBP", "JPY"]:
        assert code in message


# Parametrize works for error cases too. Note `True`: `bool` is a subclass of `int` in Python,
# so this case guards against `fmt_number(True)` quietly returning "1.00".
@pytest.mark.parametrize("bad", ["10", None, True, [1, 2]])
def test_formatters_reject_non_numbers(bad):
    with pytest.raises(TypeError, match="Expected a number"):
        fmt_number(bad)


# Options after `*` in the signature are keyword-only. This test pins that design down: if
# someone later removes the `*`, this test fails.
def test_fmt_number_options_are_keyword_only():
    with pytest.raises(TypeError):
        fmt_number(1.0, 3)  # type: ignore[misc]


# ------------------------------------------------------------------------------------------------
# xfail: a test that's expected to fail (for now)
# ------------------------------------------------------------------------------------------------
#
# `xfail` is a marker (see the markers section of test_stats.py) for a test that fails today
# for a known reason: a bug not fixed yet, or a planned feature. The test still runs, and pytest
# reports it as "xfailed" rather than failed, so the test suite stays green. It's a way of
# writing the test now and keeping a record of the problem.
#
# `xfail_strict = true` in pyproject.toml adds a safeguard: if an xfail test starts *passing*
# (someone fixed the bug), it's reported as a failure, "XPASS(strict)". That's your prompt to
# remove the marker, so the test then guards against the bug coming back.
#
# Try it: add a `dec_mark` option to `fmt_number()` and watch this test flip to XPASS(strict).


@pytest.mark.xfail(reason="fmt_number has no `dec_mark=` argument yet")
def test_fmt_number_european_style():
    assert fmt_number(1234.5, sep_mark=".", dec_mark=",") == "1.234,50"  # type: ignore[call-arg]
