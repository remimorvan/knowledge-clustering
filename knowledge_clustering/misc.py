"""Misc functions, for emphasizing a string."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

from knowledge_clustering import cst


def emph(string: str) -> str:
    """Emphasizes a string."""
    return cst.BEGIN_EMPH + string + cst.END_EMPH


def emph_alt(string: str) -> str:
    """Alternative emphasis of a string."""
    return cst.BEGIN_EMPH_ALT + string + cst.END_EMPH
