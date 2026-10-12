from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from ._formats import fmt_currency, fmt_number, fmt_percent
from ._stats import SummaryResult, summarize
from ._table import Table

try:
    __version__ = version("tinytab")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "fmt_number",
    "fmt_percent",
    "fmt_currency",
    "summarize",
    "SummaryResult",
    "Table",
]
