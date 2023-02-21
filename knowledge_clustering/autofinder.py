"""Automatically finds files in the current directory."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

import os


def autofinder():
    """Automatically finds suitable .diagnose and .notion
    files in the current working directory and yields them
    """

    for _, _, files in os.walk("."):
        for file in files:
            if os.path.basename(file).endswith(".diagnose"):
                yield ("notion", file)
            elif os.path.basename(file).endswith(".knowledge") or os.path.basename(
                file
            ).endswith(".kw"):
                yield ("knowledge", file)
