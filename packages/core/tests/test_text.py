from scholarlens_core.text import normalize_whitespace


def test_collapses_multiple_spaces() -> None:
    assert normalize_whitespace("a   b") == "a b"


def test_collapses_newlines_and_tabs() -> None:
    assert normalize_whitespace("a\n\nb\tc") == "a b c"


def test_strips_edges() -> None:
    assert normalize_whitespace("  halo  ") == "halo"
