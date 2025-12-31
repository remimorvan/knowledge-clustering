"""
Add missing quotes around knowledges occuring in a TeX document.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

import re  # Regular expressions
from typing import NamedTuple, TextIO
import sys

from knowledge_clustering.knowledges import KnowledgesList, remove_redundant_files
from knowledge_clustering.tex_document import TexDocument
from knowledge_clustering import file_updater, misc, cst
from knowledge_clustering.interactor import Action, ActionList, Interactor
from knowledge_clustering.distance import distance


def app(
    tex_filename: str,
    kl_filenames: list[str],
    print_line: int,
    inp: TextIO = sys.stdin,
    out: TextIO = sys.stdout,
) -> None:
    """
    Finds knowledges defined in the knowledge file that appear in tex file without quote
    symbols. Proposes to add quotes around them.
    Args:
        tex_filename: the name of the tex file.
        kl_filenames: the names of the knowledge files.
        print_line: an integer specifying how many lines of the tex file should be printed.
        inp: input stream.
        out: output stream.
    """
    tex_hash = file_updater.hash_file(tex_filename)
    with open(tex_filename, "r", encoding="utf-8") as f:
        # tex_doc = TexDocument(f.read())
        tex_doc = f.read().replace("~", " ")
    f.close()
    kls = KnowledgesList(remove_redundant_files(kl_filenames))
    tex_document_new, new_knowledges = quote_maximal_substrings(
        tex_doc, kls, print_line, inp, out
    )
    with file_updater.AtomicUpdate(tex_filename, original_hash=tex_hash) as f:
        f.write(tex_document_new)
    f.close()
    for known_kl, new_kl in new_knowledges:
        kls.define_synonym_of(new_kl, known_kl)
    kls.write_knowledges_in_file(nocomment=True)


states = ["last char is space-ish", "comment", "save", "final"]
initial_state = {
    "last char is space-ish": True,
    "comment": False,
    "save": True,
    "final": False,
}
final_state_property = "final"


def action_tag_exec(inter: Interactor):
    inter.document.change_string("", r"%kl-cl:todo\n")
    inter.document.increment_position(len(r"%kl-cl:todo\n"))


action_tag = Action("t", "tag", action_tag_exec, False)


def action_save_and_quit_exec(inter: Interactor):
    inter.set_state("final", True)


action_save_and_quit = Action("s", "save & quit", action_save_and_quit_exec, True)


def action_quit_exec(inter: Interactor):
    inter.set_state("save", False)
    inter.set_state("final", True)


action_quit = Action("q", "quit", action_quit_exec, True)

actions_always = [action_tag, action_save_and_quit, action_quit]


def transition_check_EOF_not_reached(inter: Interactor) -> None:
    """If EOF is reached, go to final state."""
    if not inter.document.has_chars():
        inter.set_state("final", True)


def transition_check_knowledges(inter: Interactor) -> None:
    """If the last char was space-ish (not alphanumerical), tries to match the content of the
    document with an already defined knowledge. Otherwise, tries to find the next
    few words and check if it is similar to an existing knowledge. If so, proposes to
    define it as a synonym, and add quotes."""
    if not inter.has_state("last char is space-ish"):
        return
    if matches := inter.document.startswith(inter.get_register("kls")):
        # Get the maximal match (any other match will be a prefix)
        maximal_match = matches[0]
        for match in matches[1:]:
            if len(match) > len(maximal_match):
                maximal_match = match

        def action_add_quotes_exec(inter: Interactor):
            raise NotImplementedError

        action_add_quotes = Action("y", "Add quotes", action_add_quotes_exec, False)

        def action_dont_add_quotes_exec(inter: Interactor):
            raise NotImplementedError

        action_dont_add_quotes = Action(
            "n", "Do not add quotes", action_dont_add_quotes_exec, False
        )

        actions = ActionList(
            [action_add_quotes, action_dont_add_quotes] + actions_always,
            f"Add quotes around '{maximal_match}'?",
            inter.get_input_stream(),
            inter.get_output_stream(),
        )
        while not actions.execute(inter):
            ...


def transition_update_state(inter: Interactor) -> None:
    """Defines the new state of the interactor."""
    assert inter.document.has_chars()  # Handled by transition_check_EOF_not_reached
    if inter.document.get_chars("%"):
        inter.set_state("comment", True)
    if inter.has_state("comment") and inter.document.get_chars("\n"):
        inter.set_state("comment", False)
    inter.set_state("last char is space-ish", not inter.document.get_chars().isalnum())
    inter.document.increment_position(+1)


def quote_maximal_substrings(
    tex_doc: str,
    kls: KnowledgesList,
    print_line: int,
    inp: TextIO,
    out: TextIO,
) -> tuple[str, list[tuple[str, str]]]:
    """
    Finds knowledges defined in the knowledge file that appear in tex file without quote
    symbols. Proposes to add quotes around them.

    Args:
        tex_doc: a TeX document represented as a string.
        kls: list of knowledges.
        print_line: an integer specifying how many lines of the tex file should be printed.
        inp: input stream.
        out: output stream.
    """
    raise NotImplementedError("Use tex_document to work on clean tex.")
