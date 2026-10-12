# NOTE: The comments in this file are far more extensive than in a real test suite; they're here
# because this is an educational repository. See tests/README.md for a guided reading order.

# Tests for the package as a whole, rather than one module: its version and its public API
# (both defined in tinytab/__init__.py). This is the one test file that doesn't map to a single
# module.
#
# Tests like these are cheap, and they catch packaging mistakes that would otherwise only show up
# for users after a release.

import tinytab


# The version comes from git tags via setuptools_scm, read from the installed package's metadata
# (see `__init__.py`). If that metadata is missing (say the package was never properly
# installed) `__version__` falls back to "0.0.0", so this test catches a broken setup.
def test_version_is_set():
    assert tinytab.__version__ != "0.0.0"


# The public API is whatever is listed in `__all__`. Pinning it down in a test means names can't
# be added or removed by accident: changing the public API takes a deliberate change here too,
# which shows up in code review.
def test_public_api():
    assert set(tinytab.__all__) == {
        "__version__",
        "fmt_number",
        "fmt_percent",
        "fmt_currency",
        "summarize",
        "SummaryResult",
        "Table",
    }


# A name listed in `__all__` that doesn't exist breaks `from tinytab import *`.
def test_public_api_names_exist():
    for name in tinytab.__all__:
        assert hasattr(tinytab, name), f"`{name}` is in __all__ but not defined"
