"""
Tests for the modules of knowledge_clustering defining transducers.
"""

from knowledge_clustering.interactor import Interactor


def test_interactor_simple() -> None:
    """Simple tests for the Interactor class."""
    atomic_states = ["after space", "final"]
    initial_state = {"after space": True, "final": False}
    final_states = "final"
    document = "ANAX JEHOVAH IS NOT A GOD. XOXO GRANNY. (KEEP IT TO YOURSELF)"

    def transition_change_letter(inter: Interactor) -> None:
        if inter.document.has_chars():
            c = inter.document.get_chars()
            inter.set_register("cpt", inter.get_register("cpt") + 1)
            inter.document.change_string(
                c, c.upper() if inter.has_state("after space") else c.lower()
            )

    def transition_update_state(inter: Interactor) -> None:
        if inter.document.has_chars():
            if inter.document.get_chars() in [" ", "("]:
                inter.set_state("after space", True)
            else:
                inter.set_state("after space", False)
        else:
            inter.set_state("final", True)
        inter.document.increment_position(+1)

    def transition_change_signature(inter: Interactor) -> None:
        if inter.document.startswith(["XOXO GRANNY"]):
            inter.document.change_string("XOXO GRANNY", "BEST, SNIPER")
            inter.document.increment_position(+len("BEST, SNIPER"))

    transitions = [
        transition_change_signature,
        transition_change_letter,
        transition_update_state,
    ]
    inter = Interactor(
        atomic_states,
        initial_state,
        final_states,
        transitions,
        {},
        document,
        input_file=None,
        output_file=None,
        debug=True,
    )
    assert inter.has_state("after space") and not inter.has_state("final")
    inter.set_register("cpt", 0)
    while not inter.is_in_final_state():
        inter.execute_transitions()
    assert inter.get_register("cpt") == 51
    assert (
        inter.close()
        == "Anax Jehovah Is Not A God. BEST, SNIPER. (Keep It To Yourself)"
    )
