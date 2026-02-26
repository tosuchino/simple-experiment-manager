from typing import Final

INVALID_CHARS: Final[set[str]] = set(r'\/:*?"<>| ')


def validate_safe_name(name: str) -> str:
    """Checks if the given string is safe for file and directory names.

    Raises:
        ValueError: If invalid characters or spaces are found.
    """
    if any(c in INVALID_CHARS for c in name):
        invalid_chars_display = ", ".join(sorted(INVALID_CHARS))
        raise ValueError(
            f"Invalid characters or spaces found in: '{name}'. "
            f"Prohibited: {invalid_chars_display}"
        )
    return name


def ensure_unique_list(items: list[str]) -> list[str]:
    """Removes duplicate elements from the list while preserving the original order."""
    return list(dict.fromkeys(items))
