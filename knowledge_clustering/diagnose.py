"""
Functions for handling the .diagnose files.
"""

from __future__ import annotations

from typing import Callable, Generator


_SEPARATION_HEADING_KL_BLOCK = "************************"


def automata_line(state: int, line: str) -> tuple[int, str | None]:
    """
    Transition function of a transducers parsing knowledges from a diagnose file,
    which is read line by line.

    Args:
            state: the curring state of the automata, with the following semantic:
                    0: waiting for knowledge block;
                    1: seen the heading of a knowledge block;
                    2: we are in a knowledge block.
            line: a line of the .diagnose document.

    Returns:
            a pair (state, kl) where state is the new state of the automaton,
            and kl is either None, or a knowledge parsed while reading the line given as input.
    """
    if state == 0 and "Undefined knowledges" in line:
        return 1, None
    if state == 1 and _SEPARATION_HEADING_KL_BLOCK in line:
        return 2, None
    if (state == 2 or state == 0) and _SEPARATION_HEADING_KL_BLOCK in line:
        return 0, None
    if state == 2 and "| " in line:
        s = (line.split("| ", 1)[1]).split("\n", 1)[0]
        return 2, s
    return state, None


def unroll(
    automata: Callable[[int, str], tuple[int, str | None]],
    initial_state: int,
    str_input: list[str],
) -> Generator[str | None, None, None]:
    """Builds a generator object from the transition function of a transducer."""
    state: int = initial_state
    z: str | None
    for y in str_input:
        state, z = automata(state, y)
        yield z


def parse(filename: str) -> list[str]:
    """
    Parses a diagnose file and returns the knowledges it contains.

    Args:
            filename: the name of the .diagnose file.

    Returns:
            a list of knowledges.
    """
    with open(filename) as f:
        list_notions = []
        for notion in unroll(automata_line, 0, f.readlines()):
            if notion is not None and notion not in list_notions:
                list_notions.append(notion)
    return list(list_notions)
