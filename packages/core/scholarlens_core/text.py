def normalize_whitespace(text: str) -> str:
    """Ubah semua rangkaian whitespace (spasi, tab, newline) menjadi satu spasi."""
    return " ".join(text.split())
