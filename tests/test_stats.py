# NOTE: The comments in this file are far more extensive than in a real test suite; they're here
# because this is an educational repository. See tests/README.md for a guided reading order.

# Tests for tinytab/_stats.py.

import dataclasses
import math

import pytest

from tinytab import SummaryResult, summarize

# ------------------------------------------------------------------------------------------------
# Basics
# ------------------------------------------------------------------------------------------------


# A common shape for a test is "arrange, act, assert", with a blank line between each part:
# set up the inputs, call the code under test, then check what came back.
#
# Several asserts in one test are fine when they check one behavior together. Note that pytest
# stops at the first failing assert in a test.
def test_summarize_basic():
    values = [1, 2, 3, 4]

    result = summarize(values)

    assert result.n == 4
    assert result.mean == 2.5
    assert result.min == 1
    assert result.max == 4


# Edge cases are where bugs hide. With one value the `n - 1` denominator would be zero, so the
# code handles that case specially, and the test makes sure it stays handled.
def test_summarize_single_value():
    assert summarize([7]).sd == 0.0


# ------------------------------------------------------------------------------------------------
# Floats: use pytest.approx
# ------------------------------------------------------------------------------------------------
#
# Computers store most decimal fractions inexactly, so arithmetic picks up tiny errors:
#
#   >>> 0.1 + 0.2
#   0.30000000000000004
#
# Comparing floats with `==` therefore fails for results that are "correct". `pytest.approx`
# compares within a tolerance instead. By default a value passes if it's within a relative
# tolerance of 1e-6 (one part in a million) OR an absolute tolerance of 1e-12 of the expected.


def test_float_arithmetic_is_inexact():
    total = 0.1 + 0.2

    assert total != 0.3
    assert total == pytest.approx(0.3)


def test_summarize_mean_of_floats():
    result = summarize([0.1, 0.2])

    assert result.mean == pytest.approx(0.15)


# Choose the tolerance to match how precise the expected value is. Here the expected standard
# deviation was worked out by hand to 6 significant figures, so ask for that precision with `rel=`.
def test_summarize_sd_of_floats():
    result = summarize([0.1, 0.2])

    assert result.sd == pytest.approx(0.0707107, rel=1e-5)


# Comparing to zero is a special case: a relative tolerance is a fraction *of the expected value*,
# so it's useless when that's 0. The absolute tolerance (default 1e-12, or set with `abs=`)
# handles it. Here three identical values should give an SD of exactly 0, but rounding errors in
# the mean produce about 1.7e-17 instead.
def test_summarize_sd_of_identical_values():
    result = summarize([0.1, 0.1, 0.1])

    assert result.sd != 0
    assert result.sd == pytest.approx(0)


# `approx` also works on lists, tuples, and dicts of numbers, comparing element by element.
def test_summarize_several_floats_at_once():
    result = summarize([0.1, 0.2, 0.3])

    assert [result.mean, result.min, result.max] == pytest.approx([0.2, 0.1, 0.3])


# ------------------------------------------------------------------------------------------------
# Result objects
# ------------------------------------------------------------------------------------------------
#
# `summarize()` returns a `SummaryResult` (a frozen dataclass) instead of a plain dict. Besides
# the values, its behavior is part of the API too, so test that as well.


def test_summarize_returns_a_result_object():
    assert isinstance(summarize([1, 2, 3]), SummaryResult)


# "Frozen" means the fields can't be changed after the object is created, so results can't be
# modified by accident.
def test_summarize_result_is_immutable():
    result = summarize([1, 2, 3])

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.mean = 0  # type: ignore[misc]


# A readable, deterministic repr is what users see when they print a result or look at it in a
# notebook, so pin it down.
def test_summarize_repr():
    expected = "SummaryResult(n=4, mean=2.5, sd=1.291, min=1, max=4)"

    assert repr(summarize([1, 2, 3, 4])) == expected


# ------------------------------------------------------------------------------------------------
# Errors and warnings
# ------------------------------------------------------------------------------------------------
#
# (`pytest.raises` is introduced in the errors section of test_formats.py.)


def test_summarize_empty_raises():
    with pytest.raises(ValueError, match="no non-missing values"):
        summarize([])


# Warnings work much the same way as errors, with `pytest.warns`.
#
# This matters more than usual here, because pyproject.toml sets `filterwarnings = ["error"]`:
# any warning that a test doesn't expect makes it fail. So a test whose code is supposed to warn
# must say so with `pytest.warns`. (Try deleting the `with` line to see the failure.)
def test_summarize_drops_missing_with_warning():
    with pytest.warns(UserWarning, match="Dropped 2 missing"):
        result = summarize([1, None, 3, math.nan])

    assert result.n == 2
    assert result.mean == 2


# ------------------------------------------------------------------------------------------------
# Markers: tagging tests
# ------------------------------------------------------------------------------------------------
#
# A marker is a label attached to a test with `@pytest.mark.<name>`. Some are built into pytest
# and change how the test runs (`parametrize`, `xfail`, `skipif`). Others are your own labels,
# used to select groups of tests from the command line with `-m`.
#
# `slow` is our own marker. Custom markers must be declared under `markers` in pyproject.toml;
# with `--strict-markers` on, a typo like `@pytest.mark.slwo` is an error, not a silently
# ignored label.
#
# pyproject.toml also adds `-m "not slow"` to every run, so this test is skipped (pytest reports
# it as "deselected") unless you ask for it. That keeps the everyday test run fast. Real projects
# use markers the same way for tests that need something special: a network connection, a
# browser, a GPU.
#
# Try it:
#
#   pytest -m slow                  # only the tests marked slow
#   pytest -m ""                    # everything (overrides the default `-m "not slow"`)
#   pytest -m "not slow"            # `-m` takes expressions with `and`, `or`, and `not`
#   pytest --markers                # list all the markers, built-in and ours


@pytest.mark.slow
def test_summarize_large_input():
    values = list(range(10_000_000))

    result = summarize(values)

    assert result.mean == pytest.approx(4_999_999.5)
