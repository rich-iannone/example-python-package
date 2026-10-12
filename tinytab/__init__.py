# NOTE: The comments in this package are far more extensive than in real library code; they're here
# because this is an educational repository. In a real project, comments are kept for the
# non-obvious: why the code does something, not what it does.

# `__init__.py` makes the `tinytab` folder a package, and runs when someone writes
# `import tinytab`. Here it does two jobs: it defines the package's public API, and it sets
# `__version__`.

# Makes all type hints in this file lazily evaluated strings, so newer syntax like `X | None`
# works on older Pythons and hints never cost anything at import time. Every source file in the
# package starts with it (practices doc, item 15).
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

# The implementation lives in private modules (leading underscore, practices doc item 14).
# Users import everything from `tinytab` itself, so the modules can be reorganized later
# without breaking anyone's code: `from tinytab import Table`, never
# `from tinytab._table import Table`.
from ._formats import fmt_currency, fmt_number, fmt_percent
from ._stats import SummaryResult, summarize
from ._table import Table

# The version isn't written anywhere in the source. setuptools_scm works it out from git tags
# when the package is built or installed, and stores it in the installed package's metadata,
# which `importlib.metadata.version()` reads back here.
try:
    __version__ = version("tinytab")
# If the package was never installed (say, someone runs code straight from a copy of the source
# folder), there's no metadata to read. Fall back to a placeholder rather than failing to import.
# `# pragma: no cover` tells coverage not to count this branch as missed, since the tests always
# run against an installed package.
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

# `__all__` is the definitive list of the public API: if a name isn't here, it isn't public.
# It controls what `from tinytab import *` imports, tells type checkers and editors which names
# are meant to be used, and is what documentation tools (like Great Docs) use to decide what to
# document. tests/test_package.py checks that this list doesn't change by accident.
__all__ = [
    "__version__",
    "fmt_number",
    "fmt_percent",
    "fmt_currency",
    "summarize",
    "SummaryResult",
    "Table",
]
