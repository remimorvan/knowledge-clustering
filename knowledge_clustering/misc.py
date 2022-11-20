from __future__ import annotations

_BEGIN_EMPH: str = "\033[1m\033[95m"
_BEGIN_EMPH_ALT: str = "\033[1m\033[92m"
_BEGIN_EMPH_BOLD: str = "\033[1m"
_END_EMPH: str = "\033[0m"


def emph(string: str) -> str:
    """Emphasizes a string."""
    return _BEGIN_EMPH + string + _END_EMPH


def emph_alt(string: str) -> str:
    """Alternative emphasis of a string."""
    return _BEGIN_EMPH_ALT + string + _END_EMPH
