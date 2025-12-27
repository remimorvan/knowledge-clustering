"""
Tests for the modules of knowledge_clustering defining transducers.
"""

from knowledge_clustering.interactor import Interactor


# def test_interactor_execute() -> None:
#     """Tests the actions & interface."""

#     def incr_state(inter: Interactor, step=1) -> None:
#         assert inter.current_state not in inter.final_states
#         inter.current_state += step

#     ax = Action(
#         "X", "next", lambda i: (i.current_state not in i.final_states), incr_state
#     )
#     ay = Action(
#         "Y",
#         "prev",
#         lambda i: (i.current_state not in i.final_states),
#         lambda i: incr_state(i, step=-1),
#     )
#     inter = Interactor([0, 1, 2], 0, [2], [ax, ay], "", None)
#     assert ax.is_feasible(inter) and ay.is_feasible(inter)
#     ax.execute(inter)
#     assert ax.is_feasible(inter) and ay.is_feasible(inter)
#     ay.execute(inter)
#     ax.execute(inter)
#     ax.execute(inter)
#     assert not ax.is_feasible(inter)


def test_interactor_simple() -> None:
    """Simple tests for the Interactor class."""
    atomic_states = ["after space", "final"]
    initial_state = {"after space": True, "final": False}
    final_states = "final"
    document = "ANAX JEHOVAH IS NOT A GOD. XOXO GRANNY. (KEEP IT TO YOURSELF)"
    input_file = None

    def transition_change_letter(inter: Interactor) -> None:
        if inter.document_has_char():
            c = inter.document_get_char()
            inter.update_document(
                c, c.upper() if inter.has_state("after space") else c.lower()
            )

    def transition_update_state(inter: Interactor) -> None:
        if inter.document_has_char():
            if inter.document_get_char() in [" ", "("]:
                inter.set_state("after space", True)
            else:
                inter.set_state("after space", False)
        else:
            inter.set_state("final", True)
        inter.increment_position(+1)

    def transition_change_signature(inter: Interactor) -> None:
        if inter.document_startswith(["XOXO GRANNY"]):
            inter.update_document("XOXO GRANNY", "BEST, SNIPER")
            inter.increment_position(+len("BEST, SNIPER"))

    transitions = [
        transition_change_signature,
        transition_change_letter,
        transition_update_state,
    ]
    inter = Interactor(
        atomic_states, initial_state, final_states, transitions, document, input_file
    )
    assert inter.has_state("after space") and not inter.has_state("final")
    while not inter.is_in_final_state():
        inter.execute_transitions()
    assert (
        inter.close()
        == "Anax Jehovah Is Not A God. BEST, SNIPER. (Keep It To Yourself)"
    )
