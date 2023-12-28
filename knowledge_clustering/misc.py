"""Misc functions, for emphasizing a string."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9


BEGIN_EMPH: str = "\033[1m\033[95m"
BEGIN_EMPH_ALT: str = "\033[1m\033[92m"
BEGIN_BOLD: str = "\033[1m"
BEGIN_RED: str = "\033[31m"
BEGIN_ORANGE: str = "\033[33m"
BEGIN_GREEN: str = "\033[32m"
END_EMPH: str = "\033[0m"


def emph(string: str) -> str:
    """Emphasizes a string."""
    return BEGIN_EMPH + string + END_EMPH


def emph_alt(string: str) -> str:
    """Alternative emphasis of a string."""
    return BEGIN_EMPH_ALT + string + END_EMPH


def add_red(string: str) -> str:
    """Puts a string in red."""
    return BEGIN_RED + string + END_EMPH


def add_orange(string: str) -> str:
    """Puts a string in orange."""
    return BEGIN_ORANGE + string + END_EMPH


def add_green(string: str) -> str:
    """Puts a string in green."""
    return BEGIN_GREEN + string + END_EMPH


def add_bold(string: str) -> str:
    """Puts a string in bold."""
    return BEGIN_BOLD + string + END_EMPH
