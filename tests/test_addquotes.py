"""
Tests for the modules of knowledge_clustering on which the addquotes command is based.
"""

import os
import shutil

from knowledge_clustering.add_quotes import app as app_addquotes


def test_app_addquotes() -> None:
    """Tests the addquotes command."""
    shutil.copy("tests/.ordinal.tex.original", "tests/ordinal.tex")
    shutil.copy("tests/.ordinal-kl.tex.original", "tests/ordinal-kl.tex")
    with open("tests/yes.txt", "w", encoding="utf-8") as yes:
        yes.write("y\n" * 100)
    with open("tests/yes.txt", "r", encoding="utf-8") as inp:
        with open("tests/output_addquotes.txt", "w", encoding="utf-8") as out:
            app_addquotes("tests/ordinal.tex", "tests/ordinal-kl.tex", 1, inp, out)
    with open("tests/output_addquotes.txt", "r", encoding="utf-8") as out:
        nb_line_output = sum(1 for _ in out)
    b: bool = nb_line_output == 7
    os.remove("tests/yes.txt")
    os.remove("tests/ordinal.tex")
    os.remove("tests/ordinal-kl.tex")
    os.remove("tests/output_addquotes.txt")
    assert b
