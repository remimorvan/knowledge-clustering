"""
Define transducers classes.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9
from collections.abc import Hashable, Callable
from typing import Any, TextIO
from knowledge_clustering.misc import emph
from sys import stdin

state = Hashable


class Action:
    abbrev: str
    fullname: str
    __is_feasible: Callable[[InteractiveTransducer], bool]
    __execute: Callable[[InteractiveTransducer], InteractiveTransducer]

    def __init__(
        self,
        abbrev: str,
        fullname: str,
        is_feasible: Callable[[InteractiveTransducer], bool],
        execute: Callable[[InteractiveTransducer], InteractiveTransducer],
    ) -> None:
        self.abbrev = abbrev
        self.fullname = fullname
        self.__is_feasible = is_feasible
        self.__execute = execute

    def get_abbrev(self) -> str:
        return self.abbrev

    def __str__(self) -> str:
        return emph(self.abbrev) + " (" + self.fullname + ")"

    def is_feasible(self, interface: InteractiveTransducer) -> bool:
        return self.__is_feasible(interface)

    def execute(self, interface: InteractiveTransducer) -> InteractiveTransducer:
        return self.__execute(interface)


class InteractiveTransducer:
    states: set[state]
    current_state: state
    final_states: set[state]
    filename: str
    actions: list[Action]
    registers: dict[Hashable, Any]
    document: str
    position_in_document: int
    input_stream: TextIO
    input_stream_is_file: bool

    def __init__(
        self,
        states: list[state],
        initial_state: state,
        final_states: list[state],
        actions: list[Action],
        document: str,
        input_file: str | None = None,  # If none: read on input(), otherwise read from file
    ) -> None:
        self.states = set(states)
        self.actions = actions
        self.current_state = initial_state
        self.final_states = set(final_states)
        self.registers = {}
        self.document = document
        self.position_in_document = 0
        if input_file:
            with open(input_file, mode="r", encoding="utf-8") as f:
                self.input_stream = f
                self.input_stream_is_file = True
        else:
            self.input_stream = stdin
            self.input_stream_is_file = False

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

    def run(self) -> None:
        while self.current_state not in self.final_states:
            self.__print_context()
            act = self.__print_and_ask_actions()
            act.execute(self)

    def close(self) -> str:
        if self.input_stream_is_file:
            self.input_stream.close()
        return self.document
