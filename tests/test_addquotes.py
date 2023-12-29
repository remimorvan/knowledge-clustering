"""
Tests for the modules of knowledge_clustering on which the addquotes command is based.
"""

from pathlib import Path
import shutil

from knowledge_clustering.add_quotes import app as app_addquotes


def test_app_addquotes() -> None:
    """Tests the addquotes command."""
    shutil.copy("tests/.ordinal.tex.original", "tests/ordinal.tex")
    shutil.copy("tests/.ordinal.kl.original", "tests/ordinal.kl")
    with open("tests/yes.txt", "w", encoding="utf-8") as yes:
        yes.write("y\n" * 100)
    with open("tests/yes.txt", "r", encoding="utf-8") as inp:
        with open("tests/output_addquotes.txt", "w", encoding="utf-8") as out:
            app_addquotes("tests/ordinal.tex", ["tests/ordinal.kl"], 1, inp, out)
    with open("tests/output_addquotes.txt", "r", encoding="utf-8") as out:
        nb_line_output = sum(1 for _ in out)
    b: bool = nb_line_output == 7
    p = Path("tests/")
    for filename in ["yes.txt", "ordinal.tex", "ordinal.kl", "output_addquotes.txt"]:
        (p / filename).unlink()
    assert b
