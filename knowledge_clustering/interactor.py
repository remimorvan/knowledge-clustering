"""
Defines the Interactor class.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9
from collections.abc import Hashable, Callable
from typing import Any, TextIO
from knowledge_clustering.misc import emph, add_red, add_green, add_orange, add_bold
from sys import stdin
from copy import copy

state = Hashable


class Action:
    abbrev: str
    fullname: str
    __execute: Callable[[Interactor], None]

    def __init__(
        self,
        abbrev: str,
        fullname: str,
        execute: Callable[[Interactor], None],
    ) -> None:
        self.abbrev = abbrev
        self.fullname = fullname
        self.__execute = execute

    def get_abbrev(self) -> str:
        return self.abbrev

    def __str__(self) -> str:
        return emph(self.abbrev) + " (" + self.fullname + ")"

    def execute(self, interface: Interactor) -> None:
        self.__execute(interface)


class ActionList:
    action_list: list[Action]

    def __init__(self, actions: list[Action]):
        self.actions = actions

    def get_action(self, abbrev: str) -> Action | None:
        """Given a string, returns the first action of the list with the matching abbreviation.
        If there is none, return None."""
        for act in self.actions:
            if act.get_abbrev() == abbrev:
                return act
        return None


class Interactor:
    atomic_states: list[state]
    current_state: dict[state, bool]  # a state is actually a subset of atomic_states
    final_state_property: state
    transitions: list[Callable[[Interactor], None]]
    # registers: dict[Hashable, Any]
    document: str
    document_position: int
    last_position_accessed: int
    input_stream: TextIO
    input_stream_is_file: bool

    def __init__(
        self,
        atomic_states: list[state],
        initial_state: dict[state, bool],
        final_state_property: state,
        transitions: list[Callable[[Interactor], None]],
        document: str,
        input_file: str
        | None = None,  # If none: read on input(), otherwise read from file
        debug: bool = True,
    ) -> None:
        self.atomic_states = atomic_states
        self.current_state = copy(initial_state)
        self.next_state = copy(initial_state)
        self.final_state_property = final_state_property
        self.transitions = transitions
        # self.registers = {}
        self.document = document
        self.document_next = copy(document)
        self.document_lock = False
        self.document_position = 0
        self.document_position_lock = False
        if input_file:
            with open(input_file, mode="r", encoding="utf-8") as f:
                self.input_stream = f
                self.input_stream_is_file = True
        else:
            self.input_stream = stdin
            self.input_stream_is_file = False
        self.print_state = self.print_doc = self.print_warning = debug

    def __print_context(self) -> None:
        if self.print_state:
            print(f"Current state:", end=" ")
            for s in self.atomic_states:
                has_state = self.current_state[s]
                state_str = f"{'+' if has_state else '-'}{s}"
                state_str = add_green(state_str) if has_state else add_red(state_str)
                print(state_str, end=" ")
            print("")
        if self.print_doc:
            print(f"Position in document: {self.document_position}.")

    def has_state(self, s: state) -> bool:
        """Checks whether the interactor is in a given state."""
        assert s in self.atomic_states
        return self.current_state[s]

    def set_state(self, s: state, truth: bool) -> None:
        """Set the truth value of an atomic state of the interactor.
        The change will NOT be effective until all transitions have been triggered."""
        assert s in self.atomic_states
        self.next_state[s] = truth

    def __change_state_and_doc(self) -> None:
        """Move to the next state."""
        self.current_state = copy(self.next_state)
        self.document = copy(self.document_next)
        self.document_position = self.document_position_next
        self.document_lock = False
        self.document_position_lock = False

    def is_in_final_state(self) -> bool:
        """Checks whether the interactor has reached a final state."""
        return self.current_state[self.final_state_property]

    def document_has_chars(self, len_=1) -> bool:
        """Check if the document has at least `len` next characters."""
        return self.document_position + len_ <= len(self.document)

    def document_get_chars(self, len_=1) -> str:
        """Returns the current character of the document."""
        assert self.document_has_chars(len_)
        return self.document[self.document_position : self.document_position + len_]

    def document_get_control_sequence(self) -> str | None:
        """If the current position in the document is the beginning of a LaTeX control sequence,
        returns its name. Otheriwse, returns None."""
        raise NotImplementedError

    def document_get_argument(self) -> str:
        """Parses a LaTeX argument in the document.
        On '{abc{def}foo[gh{f}]}lorem ipsum', returns 'abc{def}foo[gh{f}]',
        but on 'abc{def}foo[gh{f}]}lorem ipsum', returns 'a'."""
        raise NotImplementedError

    def document_get_begin_environment(self) -> str | None:
        r"""If the current position in the document is the beginning of a LaTeX environment,
        returns its name. Otheriwse, returns None. Treats $, \( and \[ as beginnings of
        environments, whose name is `$$`, `\(\)` and `\[\]`, respecitvely."""
        raise NotImplementedError

    def document_get_end_environment(self) -> str | None:
        r"""If the current position in the document is the end of a LaTeX environment,
        returns its name. Otheriwse, returns None. Treats $, \) and \] as beginnings of
        environments, whose name is `$$`, `\(\)` and `\[\]`, respecitvely."""
        raise NotImplementedError

    def document_startswith(self, strings: list[str]) -> list[str]:
        """Given a list of strings, returns the sublist of these strings
        that can be found at the beginning of the document (starting from the
        current position)."""
        # Todo (if necessary): improve using prefix tree.
        return [
            s for s in strings if self.document.startswith(s, self.document_position)
        ]

    def update_document(self, before: str, after: str) -> None:
        """In the document, at the current position, changes the string `before`
        into `after`."""
        assert self.document.startswith(before, self.document_position)
        if not self.document_lock:
            self.document_lock = True
            self.document_next = (
                self.document[: self.document_position]
                + after
                + self.document[self.document_position + len(before) :]
            )
        elif self.print_warning:
            print(
                add_bold(
                    add_orange(
                        "Warning: document was already changed by another transition."
                    )
                )
            )

    def execute_transitions(self) -> None:
        """Execute all transitions, in order, and updated the state and document."""
        self.__print_context()
        for fun in self.transitions:
            fun(self)
        self.__change_state_and_doc()

    def increment_position(self, delta: int):
        """Adds `delta` to the current position in the document."""
        if not self.document_position_lock:
            self.document_position_lock = True
            self.document_position_next = self.document_position + delta
        elif self.print_warning:
            print(
                add_bold(
                    add_orange(
                        "Warning: document position was already incremented by another transition."
                    )
                )
            )

    def close(self) -> str:
        """Closes the interactor, and returns the document."""
        if self.input_stream_is_file:
            self.input_stream.close()
        return self.document
