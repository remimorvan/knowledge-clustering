"""
Tests for the modules of knowledge_clustering on which the addquotes command is based.
"""

import os
import filecmp


def test_app_clustering() -> None:
    """Tests the cluster command."""
    for filename in ["ordinal-kl.tex", "ordinal.diagnose"]:
        os.system(f"cp tests/.{filename}.original tests/{filename}")
    os.system("knowledge cluster -k tests/ordinal-kl.tex -d tests/ordinal.diagnose")
    # Diagnose file should be left unchanged…
    assert filecmp.cmp(
        "tests/ordinal.diagnose", "tests/.ordinal.diagnose.original", shallow=False
    )
    # Check if knowledge file has good content
    assert filecmp.cmp(
        "tests/ordinal-kl.tex", "tests/.ordinal-kl.tex.solution", shallow=False
    )
    for filename in ["ordinal-kl.tex", "ordinal.diagnose"]:
        os.system(f"rm tests/{filename}")


def test_app_anchor() -> None:
    """Tests the anchor command."""
    os.system(f"cp tests/.ordinal.tex.original tests/ordinal.tex")
    os.system("knowledge anchor -t tests/ordinal.tex > tests/output_anchor.txt -s 200")
    nb_line_output = sum(1 for line in open("tests/output_anchor.txt"))
    b1: bool = nb_line_output == 3
    os.system("knowledge anchor -t tests/ordinal.tex > tests/output_anchor.txt -s 5")
    nb_line_output = sum(1 for line in open("tests/output_anchor.txt"))
    b2: bool = nb_line_output == 4
    os.system("rm tests/ordinal.tex tests/output_anchor.txt")
    assert b1 and b2


def test_app_addquotes() -> None:
    """Tests the addquotes command."""
    os.system(f"cp tests/.ordinal.tex.original tests/ordinal.tex")
    os.system(f"cp tests/.ordinal-kl.tex.original tests/ordinal-kl.tex")
    # with open("tests/yes.txt", "w") as f:
    #     f.write("y\n"*100)
    # f.close()
    os.system(
        f"yes | knowledge addquotes -t tests/ordinal.tex -k tests/ordinal-kl.tex > tests/output_addquotes.txt"
    )
    nb_line_output = sum(1 for line in open("tests/output_addquotes.txt"))
    b: bool = nb_line_output == 10
    os.system("rm tests/ordinal.tex tests/ordinal-kl.tex tests/output_addquotes.txt")
    assert b
