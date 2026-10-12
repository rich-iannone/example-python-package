import tinytab


def test_version_is_set():
    # Comes from git tags via setuptools_scm; "0.0.0" would mean the metadata is missing
    assert tinytab.__version__ != "0.0.0"


def test_public_api():
    # If a name isn't in `__all__`, it isn't public API
    assert set(tinytab.__all__) == {
        "__version__",
        "fmt_number",
        "fmt_percent",
        "fmt_currency",
        "summarize",
        "SummaryResult",
        "Table",
    }
    for name in tinytab.__all__:
        assert hasattr(tinytab, name)
