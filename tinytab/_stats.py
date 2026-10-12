# NOTE: The comments in this package are far more extensive than in real library code; they're here
# because this is an educational repository. See the note in __init__.py.

"""Simple summary statistics."""

from __future__ import annotations

import math
import warnings

# `Sequence` (from collections.abc) is used in the type hints instead of `list`, so callers can
# pass any sequence (a list, a tuple, ...), not just a list.
from collections.abc import Sequence
from dataclasses import dataclass

__all__ = ["SummaryResult", "summarize"]


# Results come back as a dedicated object rather than a bare tuple or dict (practices doc,
# item 19). Users get named attributes (`result.mean`) with editor autocompletion, type checkers
# know every field's type, and the class gives the result a place to grow methods later.
#
# `@dataclass` writes the boilerplate (`__init__`, `__eq__`) from the annotated fields.
# `frozen=True` makes instances immutable: assigning to a field raises an error, so a result
# can't be changed by accident after it's returned.
#
# The `*Result` name follows a naming convention used across the projects.
@dataclass(frozen=True)
class SummaryResult:
    """Summary statistics for a set of numbers, as returned by `summarize()`."""

    n: int
    mean: float
    sd: float
    min: float
    max: float

    # A custom repr: readable and deterministic, with no memory addresses. `.4g` shows four
    # significant figures, so long floats like 1.2909944487358056 print as 1.291.
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
    Summarize a list of numbers:

    ```{python}
    from tinytab import summarize

    result = summarize([3.5, 2.25, 4.0, 1.75])
    result
    ```

    Each statistic is an attribute of the result:

    ```{python}
    result.mean
    ```
    """
    # Missing values come in two forms: `None`, and NaN ("not a number", a special float). NaN
    # can't be detected with `==` (NaN isn't equal even to itself), hence `math.isnan()`.
    clean = [v for v in values if v is not None and not math.isnan(v)]
    n_dropped = len(values) - len(clean)
    if n_dropped:
        # Dropping data silently would hide problems, so tell the user through a warning.
        # Library code never prints (practices doc, item 22): warnings can be filtered, logged,
        # or turned into errors by the caller, and a test can check for them.
        #
        # `stacklevel=2` reports the warning at the line that *called* `summarize()`, in the
        # user's own code, instead of at this line inside the library.
        warnings.warn(f"Dropped {n_dropped} missing value(s).", UserWarning, stacklevel=2)

    if not clean:
        raise ValueError("Cannot summarize `values`: there are no non-missing values.")

    n = len(clean)
    mean = sum(clean) / n
    # The sample variance divides by `n - 1`, which would be zero with only one value. In that
    # case there's no spread, so the variance is defined as 0.
    var = sum((v - mean) ** 2 for v in clean) / (n - 1) if n > 1 else 0.0

    return SummaryResult(n=n, mean=mean, sd=math.sqrt(var), min=min(clean), max=max(clean))
