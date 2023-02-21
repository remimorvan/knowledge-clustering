"""
Tests for the modules of knowledge_clustering on which the addquotes command is based.
"""

import os
import filecmp


def test_app_clustering() -> None:
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
	os.system(f"cp tests/.ordinal.tex.original tests/ordinal.tex")
	os.system("knowledge anchor -t tests/ordinal.tex > tests/ordinal.anchor.output")
	nb_line_output = sum(1 for line in open('tests/ordinal.anchor.output'))
	assert(nb_line_output == 2)
	os.system("rm tests/ordinal.tex tests/ordinal.anchor.output")