"""
Tests for the modules of knowledge_clustering on which the anchor command is based.
"""

import os
import shutil

from knowledge_clustering.add_anchor import app as app_anchor


def test_app_anchor() -> None:
    """Tests the anchor command."""
    shutil.copy("tests/.ordinal.tex.original", "tests/ordinal.tex")
    with open("tests/output_anchor.txt", "w", encoding="utf-8") as out:
        app_anchor("tests/ordinal.tex", 200, out)
    nb_line_output = sum(1 for line in open("tests/output_anchor.txt"))
    b1: bool = nb_line_output == 3
    with open("tests/output_anchor.txt", "w", encoding="utf-8") as out:
        app_anchor("tests/ordinal.tex", 5, out)
    with open("tests/output_anchor.txt", "r", encoding="utf-8") as out:
        nb_line_output = sum(1 for _ in out)
    b2: bool = nb_line_output == 4
    os.remove("tests/ordinal.tex")
    os.remove("tests/output_anchor.txt")
    assert b1 and b2
