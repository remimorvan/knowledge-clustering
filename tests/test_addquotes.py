"""
Tests for the modules of knowledge_clustering on which the addquotes command is based.
"""

from pathlib import Path
import shutil

from knowledge_clustering.add_quotes import app as app_addquotes
from knowledge_clustering.add_quotes import Action, Interface


def test_interface() -> None:
    """Tests the actions & interface."""

    def incr_state(inter: Interface, step=1) -> None:
        assert not (inter.current_state in inter.final_states)
        inter.current_state += step

    ax = Action(
        "X", "next", lambda i: (not (i.current_state in i.final_states)), incr_state
    )
    ay = Action(
        "Y",
        "prev",
        lambda i: (not (i.current_state in i.final_states)),
        lambda i: incr_state(i, step=-1),
    )
    inter = Interface([0, 1, 2], 0, [2], [ax, ay])
    assert ax.is_feasible(inter) and ay.is_feasible(inter)
    ax.execute(inter)
    assert ax.is_feasible(inter) and ay.is_feasible(inter)
    ay.execute(inter)
    ax.execute(inter)
    ax.execute(inter)
    assert not ax.is_feasible(inter)


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
