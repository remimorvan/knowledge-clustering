"""Misc functions, for emphasizing a string."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

from knowledge_clustering import cst


def emph(string: str) -> str:
    """Emphasizes a string."""
    return cst.BEGIN_EMPH + string + cst.END_EMPH


def emph_alt(string: str) -> str:
    """Alternative emphasis of a string."""
    return cst.BEGIN_EMPH_ALT + string + cst.END_EMPH


def print_red(string: str) -> str:
    """Prints a string in red."""
    return cst.BEGIN_RED + string + cst.END_EMPH


def print_orange(string: str) -> str:
    """Prints a string in orange."""
    return cst.BEGIN_ORANGE + string + cst.END_EMPH


def print_green(string: str) -> str:
    """Prints a string in green."""
    return cst.BEGIN_GREEN + string + cst.END_EMPH
