# NOTE: The comments in this package are far more extensive than in real library code; they're here
# because this is an educational repository. See the note in __init__.py.

# The module docstring (below) is the first statement in the file. It's what `help()` shows for
# the module, and documentation tools display it too.
"""Functions for formatting single values as strings."""

from __future__ import annotations

# Each module declares its own public names. `__init__.py` re-exports exactly these, so the two
# lists are kept in sync when a function is added.
__all__ = ["fmt_number", "fmt_percent", "fmt_currency"]

# A module-level constant (UPPER_CASE by convention) holding the supported currencies. Keeping
# the data in one place means the validation check and the error message below both read from
# it, so adding a currency is a one-line change.
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
}


# A private helper (leading underscore): used inside this module, and not part of the API.
# Checking arguments up front, in one shared function, means every formatter rejects bad input
# the same way, with the same helpful message.
def _check_number(x: object, arg: str = "x") -> None:
    # `bool` is a subclass of `int`, but formatting `True` as "1.00" is almost always a mistake
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        # The error message names the argument, shows the bad value, and says what was expected
        # (practices doc, item 21). `!r` formats the value with `repr()`, so a string shows up
        # with quotes ('10') and can't be mistaken for a number.
        raise TypeError(f"Expected a number for `{arg}`, got {type(x).__name__}: {x!r}")


# The `*` in the signature makes every parameter after it keyword-only: callers must write
# `fmt_number(x, decimals=0)`, not `fmt_number(x, 0)`. Calls read clearly, and options can be
# added or reordered later without breaking anyone (practices doc, item 17).
#
# The docstring uses the NumPy style (Parameters, Returns, Examples sections), which
# documentation tools turn into a formatted reference page. The `>>>` lines in Examples are
# also run as tests (`--doctest-modules` in pyproject.toml), so the examples can't go stale.
def fmt_number(x: float, *, decimals: int = 2, sep_mark: str = ",") -> str:
    """Format a number with a fixed number of decimal places and a thousands separator.

    Parameters
    ----------
    x
        The number to format.
    decimals
        The number of decimal places.
    sep_mark
        The character used to separate groups of thousands.

    Returns
    -------
    str
        The formatted number.

    Examples
    --------
    >>> fmt_number(1234.567)
    '1,234.57'
    >>> fmt_number(1234.567, decimals=0)
    '1,235'
    """
    _check_number(x)
    if decimals < 0:
        raise ValueError(f"`decimals` must be zero or greater, got {decimals!r}.")

    # Python's format mini-language does the real work: `,` adds thousands separators and
    # `.2f` gives 2 decimal places. The decimal count is itself filled in from a variable, hence
    # the nested braces: `{decimals}` becomes e.g. `2`, giving the format spec `,.2f`.
    out = f"{x:,.{decimals}f}"
    if sep_mark != ",":
        out = out.replace(",", sep_mark)
    return out


def fmt_percent(x: float, *, decimals: int = 1) -> str:
    """Format a proportion as a percentage.

    Parameters
    ----------
    x
        The proportion to format, where `1` is 100%.
    decimals
        The number of decimal places.

    Returns
    -------
    str
        The formatted percentage.

    Examples
    --------
    >>> fmt_percent(0.256)
    '25.6%'
    """
    _check_number(x)
    # Reuse `fmt_number()` rather than formatting again, so rounding and separators behave the
    # same everywhere.
    return fmt_number(x * 100, decimals=decimals) + "%"


def fmt_currency(x: float, *, currency: str = "USD") -> str:
    """Format a number as a currency value.

    Parameters
    ----------
    x
        The amount to format.
    currency
        A three-letter currency code (case-insensitive). Yen values are shown without
        decimal places.

    Returns
    -------
    str
        The formatted amount, with the currency symbol.

    Examples
    --------
    >>> fmt_currency(1234.5)
    '$1,234.50'
    >>> fmt_currency(-5, currency="gbp")
    '-£5.00'
    """
    _check_number(x)
    code = currency.upper()
    if code not in CURRENCY_SYMBOLS:
        # List the valid choices in the message, so the user can fix the call without having to
        # look anything up. (Joining a dict iterates over its keys.)
        valid = ", ".join(CURRENCY_SYMBOLS)
        raise ValueError(f"Unknown currency {currency!r}. Valid currencies: {valid}.")

    decimals = 0 if code == "JPY" else 2
    # Format the absolute value and put the sign in front of the symbol ("-$5.00"). Formatting
    # the negative number directly would put the sign after it ("$-5.00").
    sign = "-" if x < 0 else ""
    return f"{sign}{CURRENCY_SYMBOLS[code]}{fmt_number(abs(x), decimals=decimals)}"
