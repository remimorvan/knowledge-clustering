"""
Defines the Interactor class.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9
from collections.abc import Hashable, Callable
from typing import Any, TextIO
from knowledge_clustering.misc import emph, add_red, add_green, add_orange, add_bold
from knowledge_clustering import cst
from sys import stdin, stdout
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


action_confirm = Action("y", "Yes", lambda i: ..., False)
action_confirm_not = Action("n", "No", lambda i: ..., False)


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
            print("\t" + (act.__str__()), file=self.output_stream)
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
                    print("\t" + (act_conf.__str__()), file=self.output_stream)
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

    atomic_states: list[state]
    current_state: dict[state, bool]  # a state is actually a subset of atomic_states
    final_state_property: state
    transitions: list[Callable[[Interactor], None]]
    registers: dict[Hashable, Any]
    document: str
    document_position: int
    last_position_accessed: int
    input_stream: TextIO
    input_stream_is_file: bool
    output_stream: TextIO
    output_stream_is_file: bool

    def __init__(
        self,
        atomic_states: list[state],
        initial_state: dict[state, bool],
        final_state_property: state,
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
        self.document = document
        self.document_next = copy(document)
        self.document_lock = False
        self.document_position = 0
        self.document_position_lock = False
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
        self.print_state = self.print_doc = self.print_warning = debug

    def __print_context(self) -> None:
        if self.print_state:
            print(f"Current state:", end=" ", file=self.output_stream)
            for s in self.atomic_states:
                has_state = self.current_state[s]
                state_str = f"{'+' if has_state else '-'}{s}"
                state_str = add_green(state_str) if has_state else add_red(state_str)
                print(state_str, end=" ", file=self.output_stream)
            print("", file=self.output_stream)
        if self.print_doc:
            print(
                f"Position in document: {self.document_position}.",
                file=self.output_stream,
            )

    def __raise_warning(self, str) -> None:
        if self.print_warning:
            print(add_bold(add_orange(str)), file=self.output_stream)

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

    def document_has_chars(self, len_=1, start=0) -> bool:
        """Check if the document has at least `len` next characters."""
        return self.document_position + start + len_ <= len(self.document)

    def document_get_chars(self, len_=1, start=0) -> str:
        """Returns the current character of the document."""
        assert self.document_has_chars(len_, start)
        return self.document[
            self.document_position + start : self.document_position + start + len_
        ]

    def document_get_next_words(self, nb_words=1) -> list[str]:
        """Returns a list of strings, corresponding to the next word, the next two words, ...,
        and the next 'nb_words' words."""
        prefixes = []
        nb_prefixes = 0
        last_char_was_end_of_word = True
        pos = 0
        while nb_prefixes < nb_words and self.document_has_chars(start=pos):
            if self.document_get_chars(start=pos) in cst.MACRO_TRIGGER_END_OF_WORD:
                if not last_char_was_end_of_word:
                    prefixes.append(self.document_get_chars(len_=pos))
                    nb_prefixes += 1
                    last_char_was_end_of_word = True
            else:
                last_char_was_end_of_word = False
            pos += 1
        return prefixes

    def document_get_control_sequence(self) -> str | None:
        """If the current position in the document is the beginning of a LaTeX control sequence,
        returns its name. Otheriwse, returns None."""
        if not self.document_has_chars():
            raise EOFError("Expected a control sequence.")
        if self.document_get_chars() != "\\":
            return None
        if not self.document_get_chars(start=1).isalpha():
            # Handles CS like \+ or \?
            return self.document_get_chars(start=1)
        len_ = 0
        while (
            self.document_has_chars(start=1 + len_)
            and self.document_get_chars(start=1 + len_).isalpha()
        ):
            len_ += 1
        return self.document_get_chars(len_=len_, start=1)

    def document_get_argument(self) -> str:
        """Parses a LaTeX argument in the document.
        On '{abc{def}foo[gh{f}]}lorem ipsum', returns 'abc{def}foo[gh{f}]',
        but on 'abc{def}foo[gh{f}]}lorem ipsum', returns 'a'."""
        if not self.document_has_chars():
            raise EOFError("Expected an argument.")
        if self.document_get_chars() != "{":
            return self.document_get_chars()
        nb_braces = 1
        pos = 1
        while nb_braces > 0:
            if not self.document_has_chars(start=pos):
                raise EOFError("EOF reached while parsing an argument.")
            match self.document_get_chars(start=pos):
                case "{":
                    nb_braces += 1
                case "}":
                    nb_braces -= 1
                case _:
                    ...
            pos += 1
        return self.document_get_chars(len_=pos - 2, start=1)

    def document_get_begin_environment(self) -> str | None:
        r"""If the current position in the document is the beginning of a LaTeX environment,
        returns its name. Otherwise, returns None. Treats \( and \[ as beginnings of
        environments, whose name is `math`."""
        if self.document_get_control_sequence() == "begin":
            self.document_position += len("\\begin")
            env = self.document_get_argument()
            self.document_position -= len("\\begin")
            return env
        if self.document_startswith(["\\(", "\\["]):
            return "math"
        return None

    def document_get_end_environment(self) -> str | None:
        r"""If the current position in the document is the end of a LaTeX environment,
        returns its name. Otherwise, returns None. Treats \) and \] as ends of
        environments, whose name is `math`."""
        if self.document_get_control_sequence() == "end":
            self.document_position += len("\\end")
            env = self.document_get_argument()
            self.document_position -= len("\\end")
            return env
        if self.document_startswith(["\\)", "\\]"]):
            return "math"

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
        else:
            self.__raise_warning(
                "Warning: document was already changed by another transition."
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
        else:
            self.__raise_warning(
                "Warning: document position was already incremented by another transition."
            )

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
        return self.input_stream

    def close(self) -> str:
        """Closes the interactor, and returns the document."""
        if self.input_stream_is_file:
            self.input_stream.close()
        if self.output_stream_is_file:
            self.output_stream.close()
        return self.document
