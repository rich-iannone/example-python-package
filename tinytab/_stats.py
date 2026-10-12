"""Simple summary statistics."""

from __future__ import annotations

import math
import warnings
from collections.abc import Sequence
from dataclasses import dataclass

__all__ = ["SummaryResult", "summarize"]


@dataclass(frozen=True)
class SummaryResult:
    """Summary statistics for a set of numbers, as returned by `summarize()`."""

    n: int
    mean: float
    sd: float
    min: float
    max: float

    def __repr__(self) -> str:
        return (
            f"SummaryResult(n={self.n}, mean={self.mean:.4g}, sd={self.sd:.4g}, "
            f"min={self.min:.4g}, max={self.max:.4g})"
        )


def summarize(values: Sequence[float | None]) -> SummaryResult:
    """Compute summary statistics for a sequence of numbers.

    Missing values (`None` and NaN) are dropped with a warning.

    Parameters
    ----------
    values
        The numbers to summarize.

    Returns
    -------
    SummaryResult
        The count, mean, standard deviation (with `n - 1` denominator), minimum and maximum.

    Examples
    --------
    >>> summarize([1, 2, 3, 4])
    SummaryResult(n=4, mean=2.5, sd=1.291, min=1, max=4)
    """
    clean = [v for v in values if v is not None and not math.isnan(v)]
    n_dropped = len(values) - len(clean)
    if n_dropped:
        warnings.warn(f"Dropped {n_dropped} missing value(s).", UserWarning, stacklevel=2)

    if not clean:
        raise ValueError("Cannot summarize `values`: there are no non-missing values.")

    n = len(clean)
    mean = sum(clean) / n
    var = sum((v - mean) ** 2 for v in clean) / (n - 1) if n > 1 else 0.0

    return SummaryResult(n=n, mean=mean, sd=math.sqrt(var), min=min(clean), max=max(clean))
