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
        if inter.document_has_chars():
            c = inter.document_get_chars()
            inter.set_register("cpt", inter.get_register("cpt") + 1)
            inter.update_document(
                c, c.upper() if inter.has_state("after space") else c.lower()
            )

    def transition_update_state(inter: Interactor) -> None:
        if inter.document_has_chars():
            if inter.document_get_chars() in [" ", "("]:
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


def test_interactor_document() -> None:
    """Tests methods related to parsing the document."""
    doc = r"""This is a \emph{sample}  of a \LaTeX~document $\+A$ with \begin{center} environments! \end{center} and so on."""
    inter = Interactor(["final"], {"final": False}, "final", [], {}, doc, None, None)
    inter.document_position = 10
    assert inter.document_has_chars()
    assert inter.document_get_chars() == "\\"
    assert inter.document_get_control_sequence() == "emph"
    inter.document_position = 14
    assert inter.document_get_argument() == "h"
    assert inter.document_get_begin_environment() == None
    assert inter.document_get_end_environment() == None
    inter.document_position = 15
    assert inter.document_get_argument() == "sample"
    inter.document_position = 47
    assert inter.document_get_control_sequence() == "+"
    assert inter.document_get_begin_environment() == None
    assert inter.document_get_end_environment() == None
    inter.document_position = 57
    assert inter.document_get_begin_environment() == "center"
    assert inter.document_get_end_environment() == None
    inter.document_position = 86
    assert inter.document_get_begin_environment() == None
    assert inter.document_get_end_environment() == "center"
    inter.document_position = 99
    assert inter.document_get_next_words(nb_words=3) == ["and", "and so", "and so on"]
    assert inter.document_get_next_words(nb_words=5) == ["and", "and so", "and so on"]
    inter.document_position = 9
    assert inter.document_get_next_words(nb_words=5) == [
        " \\emph{sample}",
        " \\emph{sample}  of",
        " \\emph{sample}  of a",
        " \\emph{sample}  of a \\LaTeX",
        " \\emph{sample}  of a \\LaTeX~document",
    ]
