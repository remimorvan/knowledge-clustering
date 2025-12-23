"""
Add missing quotes around knowledges occuring in a TeX document.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9
from enum import Enum, Flag, auto

import re  # Regular expressions
from typing import NamedTuple, TextIO, Any
from collections.abc import Generator, Hashable, Callable
import sys

from knowledge_clustering.knowledges import KnowledgesList, remove_redundant_files
from knowledge_clustering.tex_document import TexDocument
from knowledge_clustering import file_updater, misc, cst

state = Hashable


class Action:
    abbrev: str
    fullname: str
    __is_feasible: Callable[[Interface], bool]
    __execute: Callable[[Interface], Interface]

    def __init__(
        self,
        abbrev: str,
        fullname: str,
        is_feasible: Callable[[Interface], bool],
        execute: Callable[[Interface], Interface],
    ) -> None:
        self.abbrev = abbrev
        self.fullname = fullname
        self.__is_feasible = is_feasible
        self.__execute = execute

    def get_abbrev(self) -> str:
        return self.abbrev

    def __str__(self) -> str:
        return misc.emph(self.abbrev) + " (" + self.fullname + ")"

    def is_feasible(self, interface: Interface) -> bool:
        return self.__is_feasible(interface)

    def execute(self, interface: Interface) -> Interface:
        return self.__execute(interface)


class Interface:
    states: set[state]
    current_state: state
    final_states: set[state]
    filename: str
    actions: list[Action]
    registers: dict[Hashable, Any]

    def __init__(
        self,
        states: list[state],
        initial_state: state,
        final_states: list[state],
        actions: list[Action],
    ) -> None:
        self.states = set(states)
        self.actions = actions
        self.current_state = initial_state
        self.final_states = set(final_states)
        self.registers = {}

    def get_action_from_abbrev(self, abbrev: str) -> Action:
        for act in self.actions:
            if act.get_abbrev() == abbrev:
                return act
        raise KeyError(abbrev)

    def get_available_actions(self) -> list[Action]:
        """Returns actions available in the current state."""
        return [act for act in self.actions if act.is_feasible(self)]

    def __print_context(self) -> None:
        print(f"Current state: {self.current_state}")

    def __print_and_ask_actions(self) -> Action:
        act: Action | None = None
        while not act:
            for act in self.get_available_actions():
                print(act, end=" ")
            try:
                inp = input()
                act = self.get_action_from_abbrev(inp)
            except KeyError:
                print(f"'{inp}' does not correspond to a valid action.")
                act = None
        return act

    def interact(self) -> None:
        while not self.current_state in self.final_states:
            self.__print_context()
            act = self.__print_and_ask_actions()
            act.execute(self)


class NewKL(NamedTuple):
    """
    Object storing a new knowledge, together with its starting and ending point in some TeX
    document, together with a smaller knowledge, that is already known, and is a substring of
    the knowledge.
    """

    kl_origin: str
    start_origin: int
    end_origin: int
    kl: str
    start: int
    end: int


class AddQuote(NamedTuple):
    """
    Stores the starting and ending indexes of the occurence of some knowledge in a TeX document.
    """

    kl: str
    start: int
    end: int


def ask_consent(message: str, inp: TextIO, out: TextIO):
    """
    Asks whether the user wants to do an action, after printing the string `message`.
    Returns a boolean.
    """
    print(message, file=out)
    ans = inp.readline().rstrip("\n")
    return ans.lower() in ["y", "yes"]


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
        tex_doc = TexDocument(f.read())
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


def add_quote(
    tex_doc: TexDocument,
    operations: list[NewKL | AddQuote],
    print_line: int,
    inp: TextIO,
    out: TextIO,
) -> tuple[str, list[tuple[str, str]]]:
    """
    In the TeX document, for every operation of type AddQuote, proposes to add quotes before
    and after the match with the knowledge.
    For every operation of type NewKL, proposes to define a new knowledge, and to add
    quotes before and after the match.

    Args:
        tex_doc: a TeX document.
        operations: a list of operations, whose type is either NewKL or AddQuote.
        print_line: an integer specifying how many lines of the tex file should be printed.
        inp: an input stream.
        out: an output stram.
    Given a tex code, and a list of triples (_, start, end), add a quote before the
    start and after the end. If the boolean interactive if true, asks the user
    if they want to add quotes: moreover, print the print_line lines preceding
    the match before asking the user's input.
    """
    result: str = ""
    new_knowledges: list[tuple[str, str]] = []
    ignore_synonym = []
    ignore_subknowledge = []
    operations.sort(key=lambda x: x.start)
    operations_addquote: list[AddQuote] = []
    for op in operations:
        if isinstance(op, NewKL):
            if op.kl not in ignore_synonym:
                if op.kl not in [k for (_, k) in new_knowledges]:
                    # Propose to the user to define a synonym
                    tex_doc.print(op.start, op.end, print_line, out)
                    message = (
                        f"Do you want to add `{misc.emph_alt(op.kl)}` as a synonym "
                        f"of `{misc.emph_alt(op.kl_origin)}` and add quotes? [y/n] "
                    )
                    if ask_consent(message, inp, out):
                        # Adds op.kl as a new knowledge, defined as a synonym of op.kl_origin
                        new_knowledges.append((op.kl_origin, op.kl))
                        operations_addquote.append(AddQuote(op.kl, op.start, op.end))
                        # Removes any operations occuring on a substring of our new knowledge
                        for op2 in operations:
                            if isinstance(op2, AddQuote):
                                if op.start <= op2.start and op2.end <= op.end:
                                    operations.remove(op2)
                    else:
                        # From this point, do not propose again to define op.kl as a new knowledge.
                        ignore_synonym.append(op.kl)
                        if (
                            op.kl_origin
                            == tex_doc.tex_code[op.start_origin : op.end_origin + 1]
                        ):
                            # Propose to the user to add quotes around the original knowledge
                            # instead, if we have a precise match.
                            if ask_consent(
                                f"Add quotes around `{misc.emph(op.kl_origin)}` instead? [y/n] ",
                                inp,
                                out,
                            ):
                                operations_addquote.append(
                                    AddQuote(
                                        op.kl_origin, op.start_origin, op.end_origin
                                    )
                                )
                            else:
                                ignore_subknowledge.append(op.kl)
                    print("", file=out)
                else:
                    # If op.kl was already accepted as a synonym earlier, treat it
                    # as a regular knowledge
                    op = AddQuote(op.kl, op.start, op.end)
            elif op.kl not in ignore_subknowledge:
                # If the user doesn't want op.kl as a synonym but might want
                # to add quotes around op.kl_origin
                op = AddQuote(op.kl_origin, op.start_origin, op.end_origin)
        elif isinstance(op, AddQuote):
            tex_doc.print(op.start, op.end, print_line, out)
            if ask_consent("Add quotes? [y/n] ", inp, out):
                operations_addquote.append(op)
            print("", file=out)
    add_quote_before = [tex_doc.pointer[op.start] for op in operations_addquote]
    add_quote_after = [tex_doc.pointer[op.end] for op in operations_addquote]
    # Simply add quotes before and after every positions corresponding to the beginning / end of
    # a match with a knowledge.
    for i, char in enumerate(tex_doc.tex_code):
        if i in add_quote_before:
            result += '"'
        result += char
        if i in add_quote_after:
            result += '"'
    print(
        f"Added {len(operations_addquote)} pair"
        + ("s" if len(operations_addquote) > 1 else "")
        + f" of quotes. Defined {len(new_knowledges)} synonym"
        + ("s." if len(new_knowledges) > 1 else "."),
        file=out,
    )
    return result, new_knowledges


def quote_maximal_substrings(
    tex_doc: TexDocument,
    kls: KnowledgesList,
    print_line: int,
    inp: TextIO,
    out: TextIO,
) -> tuple[str, list[tuple[str, str]]]:
    """
    Finds knowledges defined in the knowledge file that appear in tex file without quote
    symbols. Proposes to add quotes around them.

    Args:
        tex_doc: a TeX document.
        kls: list of knowledges.
        print_line: an integer specifying how many lines of the tex file should be printed.
        inp: input stream.
        out: output stream.
    """

    def stop_expanding(char):
        return not char.isalpha()

    ignore_position = [False] * tex_doc.length
    add_quote_location: list[NewKL | AddQuote] = []
    for ignore_case in [False, True]:
        # Start the algo by being case sensitive, then run it while being insensitive.
        for s1 in kls.get_sorted_knowledges():
            match_list = (
                re.finditer(re.escape(s1), tex_doc.tex_cleaned, re.IGNORECASE)
                if ignore_case
                else re.finditer(re.escape(s1), tex_doc.tex_cleaned)
            )
            for match in match_list:
                start, end = match.start(), match.end() - 1
                if not ignore_position[start]:
                    # Ignore every infix of s1 that is also a substring of the list
                    for i in range(start, end + 1):
                        ignore_position[i] = True
                    for s2 in kls.dependency[s1]:
                        for submatch in re.finditer(
                            re.escape(s2), tex_doc.tex_cleaned[start : end + 1]
                        ):
                            ignore_position[start + submatch.start()] = True
                    # Check if s1 is precedeed by quotes, if not, either check
                    # if we can define a new knowledge, or add the match to the
                    # list of quotes to add.
                    if not any(
                        tex_doc.tex_cleaned.endswith(beg_kl, 0, start)
                        and tex_doc.tex_cleaned.startswith(end_kl, end + 1)
                        for (beg_kl, end_kl) in cst.KL_DELIMITERS
                    ):
                        start2, end2 = start, end
                        while start2 > 0 and not stop_expanding(
                            tex_doc.tex_cleaned[start2 - 1]
                        ):
                            start2 -= 1
                        while end2 + 1 < len(
                            tex_doc.tex_cleaned
                        ) and not stop_expanding(tex_doc.tex_cleaned[end2 + 1]):
                            end2 += 1
                        # text_cleaned[start2: end2 + 1] is the maximal substring
                        # containing text_cleaned[start, end + 1] = s1 as a factor,
                        # and obtained by only addings letters (no space).
                        new_kl = tex_doc.tex_cleaned[start2 : end2 + 1]
                        if s1 != new_kl:
                            # Propose to add new_kl as a new knowledge
                            add_quote_location.append(
                                NewKL(s1, start, end, new_kl, start2, end2)
                            )
                        else:
                            add_quote_location.append(AddQuote(s1, start, end))
    return add_quote(tex_doc, add_quote_location, print_line, inp, out)
