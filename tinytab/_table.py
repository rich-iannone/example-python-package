"""A tiny table that can be formatted and rendered as text or HTML."""

from __future__ import annotations

import csv
from collections.abc import Callable, Mapping, Sequence
from html import escape
from pathlib import Path
from typing import Any

__all__ = ["Table"]


class Table:
    """A small, column-oriented table.

    Parameters
    ----------
    data
        A dictionary mapping column names to sequences of values. All columns must have the
        same length.

    Examples
    --------
    >>> tbl = Table({"item": ["coffee", "bagel"], "price": [3.5, 2.25]})
    >>> tbl
    <Table: 2 rows x 2 columns>
    """

    def __init__(self, data: Mapping[str, Sequence[Any]]):
        lengths = {k: len(v) for k, v in data.items()}
        if len(set(lengths.values())) > 1:
            raise ValueError(f"All columns must have the same length, got lengths {lengths}.")

        self._data: dict[str, list[Any]] = {k: list(v) for k, v in data.items()}
        self._formatters: dict[str, Callable[[Any], str]] = {}

    @property
    def columns(self) -> list[str]:
        """The column names."""
        return list(self._data)

    @property
    def n_rows(self) -> int:
        """The number of rows."""
        return len(next(iter(self._data.values()), []))

    def __repr__(self) -> str:
        return f"<Table: {self.n_rows} rows x {len(self.columns)} columns>"

    def _repr_html_(self) -> str:
        return self.as_html()

    def fmt(self, column: str, fn: Callable[[Any], str]) -> Table:
        """Attach a formatting function to a column.

        Parameters
        ----------
        column
            The column to format.
        fn
            A function that takes a single value and returns a string. Missing values (`None`)
            are rendered as empty cells and are never passed to `fn`.

        Returns
        -------
        Table
            A new table; the original is not modified.

        Examples
        --------
        >>> from tinytab import fmt_currency
        >>> tbl = Table({"price": [3.5]}).fmt("price", fmt_currency)
        >>> print(tbl.as_text())
        | price |
        |-------|
        | $3.50 |
        """
        if column not in self._data:
            raise KeyError(f"No column named {column!r}. Available columns: {self.columns}.")

        new = Table(self._data)
        new._formatters = {**self._formatters, column: fn}
        return new

    def _cell(self, column: str, i: int) -> str:
        value = self._data[column][i]
        if value is None:
            return ""
        fn = self._formatters.get(column, str)
        return fn(value)

    def _rows(self) -> list[list[str]]:
        return [[self._cell(col, i) for col in self.columns] for i in range(self.n_rows)]

    def as_text(self) -> str:
        """Render the table as a Markdown-style text table.

        Returns
        -------
        str
            The rendered table.
        """
        rows = self._rows()
        widths = [
            max(len(col), *(len(r[j]) for r in rows)) if rows else len(col)
            for j, col in enumerate(self.columns)
        ]

        def line(cells: list[str]) -> str:
            padded = (c.ljust(w) for c, w in zip(cells, widths, strict=True))
            return "| " + " | ".join(padded) + " |"

        out = [line(self.columns), "|" + "|".join("-" * (w + 2) for w in widths) + "|"]
        out += [line(r) for r in rows]
        return "\n".join(out)

    def as_html(self) -> str:
        """Render the table as an HTML `<table>`.

        Returns
        -------
        str
            The rendered table, with all values HTML-escaped.
        """
        head = "".join(f"<th>{escape(c)}</th>" for c in self.columns)
        body = "\n".join(
            "    <tr>" + "".join(f"<td>{escape(c)}</td>" for c in row) + "</tr>"
            for row in self._rows()
        )
        return (
            '<table class="tinytab">\n'
            f"  <thead>\n    <tr>{head}</tr>\n  </thead>\n"
            f"  <tbody>\n{body}\n  </tbody>\n"
            "</table>"
        )

    def to_csv(self, path: str | Path) -> None:
        """Write the table's unformatted values to a CSV file.

        Parameters
        ----------
        path
            The file to write.
        """
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            for i in range(self.n_rows):
                writer.writerow(self._data[col][i] for col in self.columns)

    @classmethod
    def from_csv(cls, path: str | Path) -> Table:
        """Read a table from a CSV file. All values are read as strings.

        Parameters
        ----------
        path
            The file to read.

        Returns
        -------
        Table
            The table read from the file.
        """
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            raise ValueError(f"No data rows found in {str(path)!r}.")
        return cls({col: [r[col] for r in rows] for col in rows[0]})
