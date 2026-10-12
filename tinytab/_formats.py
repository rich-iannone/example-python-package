"""Functions for formatting single values as strings."""

from __future__ import annotations

__all__ = ["fmt_number", "fmt_percent", "fmt_currency"]

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
}


def _check_number(x: object, arg: str = "x") -> None:
    # `bool` is a subclass of `int`, but formatting `True` as "1.00" is almost always a mistake
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise TypeError(f"Expected a number for `{arg}`, got {type(x).__name__}: {x!r}")


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
        valid = ", ".join(CURRENCY_SYMBOLS)
        raise ValueError(f"Unknown currency {currency!r}. Valid currencies: {valid}.")

    decimals = 0 if code == "JPY" else 2
    sign = "-" if x < 0 else ""
    return f"{sign}{CURRENCY_SYMBOLS[code]}{fmt_number(abs(x), decimals=decimals)}"
