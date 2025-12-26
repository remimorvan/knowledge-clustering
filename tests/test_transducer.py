"""
Tests for the modules of knowledge_clustering defining transducers.
"""

from knowledge_clustering.transducer import Action, InteractiveTransducer


def test_interactive_transducer_execute() -> None:
    """Tests the actions & interface."""

    def incr_state(inter: InteractiveTransducer, step=1) -> None:
        assert inter.current_state not in inter.final_states
        inter.current_state += step

    ax = Action(
        "X", "next", lambda i: (i.current_state not in i.final_states), incr_state
    )
    ay = Action(
        "Y",
        "prev",
        lambda i: (i.current_state not in i.final_states),
        lambda i: incr_state(i, step=-1),
    )
    inter = InteractiveTransducer([0, 1, 2], 0, [2], [ax, ay], "", None)
    assert ax.is_feasible(inter) and ay.is_feasible(inter)
    ax.execute(inter)
    assert ax.is_feasible(inter) and ay.is_feasible(inter)
    ay.execute(inter)
    ax.execute(inter)
    ax.execute(inter)
    assert not ax.is_feasible(inter)
