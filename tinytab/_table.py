# NOTE: The comments in this package are far more extensive than in real library code; they're here
# because this is an educational repository. See the note in __init__.py.

"""A tiny table that can be formatted and rendered as text or HTML."""

from __future__ import annotations

# Imports are grouped (standard library, then third-party, then this package) and sorted within
# each group. ruff's "I" rules enforce this automatically, so nobody has to think about it.
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
    Create a table from a dictionary of columns. In a notebook, or on a page like this one, a table
    displays as HTML:

    ```{python}
    from tinytab import Table

    tbl = Table({"item": ["coffee", "bagel"], "price": [3.5, 2.25]})
    tbl
    ```
    """

    # The input type is deliberately broad: `Mapping` accepts any dict-like object, and
    # `Sequence` any list-like one. (It also has to be: with `dict[str, Sequence]`, pyright's
    # strict mode rejects passing in a `dict[str, list]`, because dict types are "invariant".)
    def __init__(self, data: Mapping[str, Sequence[Any]]):
        # Validate once, up front, in the constructor (practices doc, item 21). Every method can
        # then rely on the columns having equal lengths, without checking again.
        lengths = {k: len(v) for k, v in data.items()}
        if len(set(lengths.values())) > 1:
            raise ValueError(f"All columns must have the same length, got lengths {lengths}.")

        # Copy the data into new lists, so later changes to the caller's lists can't change the
        # table behind its back. The leading underscore marks these attributes as private:
        # users go through the public properties and methods instead.
        self._data: dict[str, list[Any]] = {k: list(v) for k, v in data.items()}
        self._formatters: dict[str, Callable[[Any], str]] = {}

    # `@property` makes a method readable like an attribute (`tbl.columns`, no parentheses).
    # Users can read it but not assign to it, and it always reflects the current data.
    @property
    def columns(self) -> list[str]:
        """The column names."""
        # Dicts keep their insertion order (guaranteed since Python 3.7), so the columns come
        # out in the order they were given.
        return list(self._data)

    @property
    def n_rows(self) -> int:
        """The number of rows."""
        # The length of the first column (all columns have the same length). The `[]` default
        # handles a table with no columns at all, which has 0 rows.
        return len(next(iter(self._data.values()), []))

    # `__repr__` is what you see when you inspect the object in a console. A short summary is
    # more useful here than dumping all the data.
    def __repr__(self) -> str:
        return f"<Table: {self.n_rows} rows x {len(self.columns)} columns>"

    # Jupyter (and other notebook tools) look for a `_repr_html_()` method, and if one exists,
    # display its HTML instead of the plain repr. That's all it takes for a table to render
    # nicely in a notebook.
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
        Format the `price` column as US dollars:

        ```{python}
        from tinytab import Table, fmt_currency

        tbl = Table({"item": ["coffee", "bagel"], "price": [3.5, 2.25]})
        tbl.fmt("price", fmt_currency)
        ```

        Any function that takes a value and returns a string works as a formatter:

        ```{python}
        tbl.fmt("price", lambda x: f"{x:.1f} USD")
        ```
        """
        if column not in self._data:
            raise KeyError(f"No column named {column!r}. Available columns: {self.columns}.")

        # Return a new table instead of changing this one. That makes method chaining safe
        # (`tbl.fmt(...).fmt(...)`), and a table that's been passed around can't be changed
        # unexpectedly by someone else's code. (Great Tables' `GT` works the same way.)
        #
        # `{**old, key: value}` builds a new dict: a copy of the old one, plus one entry.
        new = Table(self._data)
        new._formatters = {**self._formatters, column: fn}
        return new

    # Private helpers do the shared work for the rendering methods below.
    def _cell(self, column: str, i: int) -> str:
        value = self._data[column][i]
        if value is None:
            return ""
        # Columns without a formatter fall back to `str`, which is itself just a function
        # from value to string.
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

        Examples
        --------
        ```{python}
        from tinytab import Table, fmt_currency

        tbl = Table({"item": ["coffee", "bagel"], "price": [3.5, 2.25]})
        print(tbl.fmt("price", fmt_currency).as_text())
        ```
        """
        rows = self._rows()
        # Each column is as wide as its longest entry, header included. (With no rows, `max()`
        # would be given a single number, which is an error, so that case is handled separately.)
        widths = [
            max(len(col), *(len(r[j]) for r in rows)) if rows else len(col)
            for j, col in enumerate(self.columns)
        ]

        # A function defined inside a method can use the method's local variables (here,
        # `widths`), which keeps this small helper next to the only code that uses it.
        def line(cells: list[str]) -> str:
            # `strict=True` makes `zip()` raise an error if the two lists differ in length,
            # instead of silently stopping at the shorter one. ruff's B905 rule asks for it.
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

        Examples
        --------
        ```{python}
        from tinytab import Table

        tbl = Table({"item": ["coffee", "bagel"], "price": [3.5, 2.25]})
        print(tbl.as_html())
        ```
        """
        # Every value is escaped (`<` becomes `&lt;`, `&` becomes `&amp;`, ...), so text from the
        # data can't be mistaken for HTML tags. Without it, a value like "<script>" would end up
        # as real markup in the page.
        head = "".join(f"<th>{escape(c)}</th>" for c in self.columns)
        body = "\n".join(
            "    <tr>" + "".join(f"<td>{escape(c)}</td>" for c in row) + "</tr>"
            for row in self._rows()
        )
        # Adjacent string literals inside parentheses are joined into one string, which keeps
        # long strings readable across several lines.
        return (
            '<table class="tinytab">\n'
            f"  <thead>\n    <tr>{head}</tr>\n  </thead>\n"
            f"  <tbody>\n{body}\n  </tbody>\n"
            "</table>"
        )

    # Paths are accepted as either a string or a `pathlib.Path`, so users can pass whichever
    # they have (including pytest's `tmp_path / "file.csv"`).
    def to_csv(self, path: str | Path) -> None:
        """Write the table's unformatted values to a CSV file.

        Parameters
        ----------
        path
            The file to write.

        Examples
        --------
        Save a table, then read it back with `Table.from_csv()`:

        ```{python}
        import tempfile
        from pathlib import Path

        from tinytab import Table

        path = Path(tempfile.mkdtemp()) / "menu.csv"
        Table({"item": ["coffee", "bagel"], "price": [3.5, 2.25]}).to_csv(path)

        print(path.read_text())
        ```
        """
        # `with` closes the file when the block ends, even if an error happens partway through.
        # `newline=""` is what the csv module needs to write line endings correctly on every
        # operating system (without it, Windows gets blank lines between rows).
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            for i in range(self.n_rows):
                writer.writerow(self._data[col][i] for col in self.columns)

    # A classmethod is called on the class itself (`Table.from_csv(path)`), and receives the
    # class as `cls`. It's the usual way to provide alternative constructors.
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

        Examples
        --------
        Save a table with `Table.to_csv()`, then read it back. CSV files don't record types, so
        every value comes back as a string:

        ```{python}
        import tempfile
        from pathlib import Path

        from tinytab import Table

        path = Path(tempfile.mkdtemp()) / "menu.csv"
        Table({"item": ["coffee", "bagel"], "price": [3.5, 2.25]}).to_csv(path)

        Table.from_csv(path)
        ```
        """
        # `DictReader` uses the header row as keys, giving one dict per data row.
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            raise ValueError(f"No data rows found in {str(path)!r}.")
        # Turn the list of row dicts into the dict of columns that `Table` expects.
        return cls({col: [r[col] for r in rows] for col in rows[0]})
