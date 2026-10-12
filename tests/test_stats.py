import dataclasses
import math

import pytest

from tinytab import summarize


def test_summarize_basic():
    result = summarize([1, 2, 3, 4])

    assert result.n == 4
    assert result.mean == 2.5
    assert result.min == 1
    assert result.max == 4


# Floating point: 0.1 + 0.2 != 0.3, so compare with pytest.approx
def test_summarize_floats():
    result = summarize([0.1, 0.2])

    assert result.mean == pytest.approx(0.15)
    assert result.sd == pytest.approx(0.0707107, rel=1e-5)


# Results are frozen dataclasses, so they can't be modified by accident
def test_summarize_result_is_immutable():
    result = summarize([1, 2, 3])

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.mean = 0  # type: ignore[misc]


def test_summarize_repr():
    expected = "SummaryResult(n=4, mean=2.5, sd=1.291, min=1, max=4)"
    assert repr(summarize([1, 2, 3, 4])) == expected


def test_summarize_single_value():
    assert summarize([7]).sd == 0.0


def test_summarize_empty_raises():
    with pytest.raises(ValueError, match="no non-missing values"):
        summarize([])


# Warnings are errors in our config (`filterwarnings = ["error"]`), so expected
# warnings must be captured explicitly
def test_summarize_drops_missing_with_warning():
    with pytest.warns(UserWarning, match="Dropped 2 missing"):
        result = summarize([1, None, 3, math.nan])

    assert result.n == 2
    assert result.mean == 2


# Markers: this is deselected by default (see `addopts` in pyproject.toml)
@pytest.mark.slow
def test_summarize_large_input():
    values = list(range(10_000_000))
    result = summarize(values)
    assert result.mean == pytest.approx(4_999_999.5)
