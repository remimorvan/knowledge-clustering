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
    __is_feasible: Callable[[Interactor], bool]
    __execute: Callable[[Interactor], Interactor]

    def __init__(
        self,
        abbrev: str,
        fullname: str,
        is_feasible: Callable[[Interactor], bool],
        execute: Callable[[Interactor], Interactor],
    ) -> None:
        self.abbrev = abbrev
        self.fullname = fullname
        self.__is_feasible = is_feasible
        self.__execute = execute

    def get_abbrev(self) -> str:
        return self.abbrev

    def __str__(self) -> str:
        return emph(self.abbrev) + " (" + self.fullname + ")"

    def is_feasible(self, interface: Interactor) -> bool:
        return self.__is_feasible(interface)

    def execute(self, interface: Interactor) -> Interactor:
        return self.__execute(interface)


class Interactor:
    atomic_states: list[state]
    current_state: dict[state, bool]  # a state is actually a subset of atomic_states
    final_state_property: state
    transitions: list[Callable[[Interactor]], None]
    # registers: dict[Hashable, Any]
    document: str
    position_in_document: int
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
    ) -> None:
        self.atomic_states = atomic_states
        self.current_state = copy(initial_state)
        self.next_state = copy(initial_state)
        self.final_state_property = final_state_property
        self.transitions = transitions
        # self.registers = {}
        self.document = document
        self.document_lock = False
        self.position_in_document = 0
        self.last_position_accessed_start = 0
        self.print_state = True
        self.print_doc = True
        self.print_warning = True
        if input_file:
            with open(input_file, mode="r", encoding="utf-8") as f:
                self.input_stream = f
                self.input_stream_is_file = True
        else:
            self.input_stream = stdin
            self.input_stream_is_file = False

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
            print(f"Position in document: {self.position_in_document}.")
            print(f"Current view of document (trunc.): {self.get_document()[:30]}")

    def has_state(self, s: state) -> bool:
        """Checks whether the interactor is in a given state."""
        assert s in self.atomic_states
        return self.current_state[s]

    def set_state(self, s: state, truth: bool) -> None:
        """Set the truth value of an atomic state of the interactor.
        The change will NOT be effective until all transitions have been triggered."""
        assert s in self.atomic_states
        self.next_state[s] = truth

    def __change_state(self) -> None:
        """Move to the next state."""
        self.current_state = copy(self.next_state)

    def is_in_final_state(self) -> bool:
        """Checks whether the interactor has reached a final state."""
        return self.current_state[self.final_state_property]

    def get_document(self):
        """Returns the document handled by the interactor, between the current position and
        the end of the document."""
        self.last_position_accessed = self.position_in_document
        return self.document[self.position_in_document :]

    def set_document(self, doc: str):
        """Updates a document. Only changes the part that was last accessed with get_document.
        At most one transition can change the document."""
        if not self.document_lock:
            self.document_lock = True
            self.document = self.document[: self.last_position_accessed] + doc
        elif self.print_warning:
            print(
                add_bold(
                    add_orange(
                        "Warning: document was already changed by another transition."
                    )
                )
            )

    def execute_transitions(self) -> None:
        self.__print_context()
        self.document_lock = False
        for fun in self.transitions:
            fun(self)
        self.__change_state()

    def increment_position(self, delta: int):
        """Adds `delta` to the current position in the document."""
        self.position_in_document += delta

    def run(self) -> None:
        while self.current_state not in self.final_states:
            self.__print_context()

    def close(self) -> str:
        if self.input_stream_is_file:
            self.input_stream.close()
        return self.document
