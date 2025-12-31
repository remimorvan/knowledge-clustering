"""
Defines the Interactor class.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9
from collections.abc import Hashable, Callable
from typing import Any, TextIO
from sys import stdin, stdout
from copy import copy

from knowledge_clustering.tex_document import TexDocument
from knowledge_clustering.misc import emph, add_red, add_green, add_orange, add_bold
from knowledge_clustering import cst

State = Hashable


class Action:
    abbrev: str
    fullname: str
    __execute: Callable[[Interactor], None]

    def __init__(
        self,
        abbrev: str,
        fullname: str,
        execute: Callable[[Interactor], None],
        requires_confirmation: bool,
    ) -> None:
        self.abbrev = abbrev.lower()
        self.fullname = fullname
        self.__execute = execute
        self.__requires_confirmation = requires_confirmation

    def get_abbrev(self) -> str:
        return self.abbrev

    def __str__(self) -> str:
        return emph(self.abbrev) + ": " + self.fullname + ""

    def execute(self, interface: Interactor) -> None:
        self.__execute(interface)

    def requires_confirmation(self) -> bool:
        return self.__requires_confirmation


action_confirm = Action("y", "Yes", lambda i: None, False)
action_confirm_not = Action("n", "No", lambda i: None, False)


class ActionList:
    actions: list[Action]
    message: str
    input_stream: TextIO
    output_stream: TextIO

    def __init__(
        self,
        actions: list[Action],
        message: str,
        input_stream: TextIO,
        output_stream: TextIO,
    ):
        self.actions = actions
        self.message = message
        self.input_stream = input_stream
        self.output_stream = output_stream

    def print_and_ask(self) -> str:
        """Asks the user's input after printing the different actions."""
        print(self.message)
        for act in self.actions:
            print("\t" + str(act), file=self.output_stream)
        return self.input_stream.readline().rstrip().lower()

    def get_action(self, abbrev: str) -> Action | None:
        """Given a string, returns the first action of the list with the matching abbreviation.
        If there is none, return None."""
        for act in self.actions:
            if act.get_abbrev() == abbrev:
                return act
        return None

    def execute(self, inter: Interactor) -> bool:
        """Prints the different actions, asks the user's input, and if it corresponds to a valid
        action, executes it. Returns a Boolean describing whether an action was executed.
        """
        abbrev = self.print_and_ask()
        act = self.get_action(abbrev)
        confirm = True
        if act:
            if act.requires_confirmation():
                print(f"Confirm action ({act.fullname})?", file=self.output_stream)
                for act_conf in [action_confirm, action_confirm_not]:
                    print("\t" + str(act_conf), file=self.output_stream)
                if self.input_stream.readline().rstrip().lower() != "y":
                    confirm = False
            if confirm:
                act.execute(inter)
        return bool(act) and confirm


class Interactor:
    """An interactor is a finite-state transducers with registers. It has atomic states,
    and at a given time, the state of the machine is a subset of these states.
    Transitions are arbitrary functions that act on the interactor.
    They are executed in order. At most one of them can change the document
    (resp. the position in the document).
    Transitions can use actions, that ask the user's input via an input stream."""

    atomic_states: list[State]
    current_state: dict[State, bool]  # a state is actually a subset of atomic_states
    final_state_property: State
    transitions: list[Callable[[Interactor], None]]
    registers: dict[Hashable, Any]
    document: TexDocument
    input_stream: TextIO
    input_stream_is_file: bool
    output_stream: TextIO
    output_stream_is_file: bool

    def __init__(
        self,
        atomic_states: list[State],
        initial_state: dict[State, bool],
        final_state_property: State,
        transitions: list[Callable[[Interactor], None]],
        registers: dict[Hashable, Any],
        document: str,
        input_file: str
        | None = None,  # If none: read on input(), otherwise read from file
        output_file: str
        | None = None,  # If none: print on stdout, otherwise read from file
        debug: bool = False,
    ) -> None:
        self.atomic_states = atomic_states
        self.current_state = copy(initial_state)
        self.next_state = copy(initial_state)
        self.final_state_property = final_state_property
        self.transitions = transitions
        self.registers = copy(registers)
        self.document = TexDocument(document)
        if input_file:
            self.input_stream = open(input_file, mode="r", encoding="utf-8")
        else:
            self.input_stream = stdin
        self.input_stream_is_file = bool(input_file)
        if output_file:
            self.output_stream = open(output_file, mode="w", encoding="utf-8")
        else:
            self.output_stream = stdout
        self.output_stream_is_file = bool(output_file)
        self.print_state = self.print_doc = debug

    def __print_context(self) -> None:
        if self.print_state:
            print("Current state:", end=" ", file=self.output_stream)
            for s in self.atomic_states:
                has_state = self.current_state[s]
                state_str = f"{'+' if has_state else '-'}{s}"
                state_str = add_green(state_str) if has_state else add_red(state_str)
                print(state_str, end=" ", file=self.output_stream)
            print("", file=self.output_stream)
        if self.print_doc:
            print(
                f"Position in document: {self.document.position}.",
                file=self.output_stream,
            )

    def has_state(self, s: State) -> bool:
        """Checks whether the interactor is in a given state."""
        assert s in self.atomic_states
        return self.current_state[s]

    def set_state(self, s: State, truth: bool) -> None:
        """Set the truth value of an atomic state of the interactor.
        The change will NOT be effective until all transitions have been triggered."""
        assert s in self.atomic_states
        self.next_state[s] = truth

    def __change_state_and_doc(self) -> None:
        """Move to the next state."""
        self.current_state = copy(self.next_state)
        self.document.apply_change()
        self.document.reset_locks()

    def is_in_final_state(self) -> bool:
        """Checks whether the interactor has reached a final state."""
        return self.current_state[self.final_state_property]

    # def document_get_next_words(self, nb_words=1) -> list[str]:
    #     """Returns a list of strings, corresponding to the next word, the next two words, ...,
    #     and the next 'nb_words' words."""
    #     prefixes = []
    #     nb_prefixes = 0
    #     last_char_was_end_of_word = True
    #     pos = 0
    #     while nb_prefixes < nb_words and self.document_has_chars(start=pos):
    #         if self.document_get_chars(start=pos) in cst.MACRO_TRIGGER_END_OF_WORD:
    #             if not last_char_was_end_of_word:
    #                 prefixes.append(self.document_get_chars(len_=pos))
    #                 nb_prefixes += 1
    #                 last_char_was_end_of_word = True
    #         else:
    #             last_char_was_end_of_word = False
    #         pos += 1
    #     return prefixes

    def execute_transitions(self) -> None:
        """Execute all transitions, in order, and updated the state and document."""
        self.__print_context()
        for fun in self.transitions:
            fun(self)
        self.__change_state_and_doc()

    def has_register(self, key: Hashable) -> bool:
        """Checks if a register exists."""
        return key in self.registers

    def get_register(self, key: Hashable) -> Any:
        """Looks up the value of a register."""
        assert self.has_register(key)
        return self.registers[key]

    def set_register(self, key: Hashable, val: Any) -> None:
        """Sets the value of a register."""
        self.registers[key] = copy(val)

    def get_input_stream(self) -> TextIO:
        """Returns the input stream of the interactor."""
        return self.input_stream
    
    def get_output_stream(self) -> TextIO:
        """Returns the outputù stream of the interactor."""
        return self.output_stream

    def close(self) -> str:
        """Closes the interactor, and returns the document."""
        if self.input_stream_is_file:
            self.input_stream.close()
        if self.output_stream_is_file:
            self.output_stream.close()
        return self.document.get_document_code()
