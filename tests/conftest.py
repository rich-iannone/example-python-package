# NOTE: The comments in this file are far more extensive than in a real test suite; they're here
# because this is an educational repository. See tests/README.md for a guided reading order.

# conftest.py is a special file that pytest loads automatically, before the tests in this folder
# (and its subfolders) run. Fixtures defined here can be used by any of those tests, just by
# naming them as a parameter. Tests never import from conftest.py. (Fixtures are introduced in
# the fixtures section of test_table.py.)

import pytest

from tinytab import Table


# The docstring is shown by `pytest --fixtures`, so it's worth writing one for shared fixtures.
@pytest.fixture
def menu():
    """A small table of cafe menu items, with one missing value in `sold`."""
    return Table(
        {
            "item": ["coffee", "bagel", "croissant"],
            "price": [3.5, 2.25, 4.0],
            "sold": [120, 45, None],
        }
    )
