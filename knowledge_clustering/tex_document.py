"""Handling a Tex document."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9
from typing import TextIO

from knowledge_clustering import misc


class TexDocument:
    """Class for handling a TeX document."""

    tex_code: str  # original TeX document
    lines: list[str]  # original tex document, split by lines
    find_line: list[
        int
    ]  # if i is an index of tex_code, then find_line[i] is its line number
    find_col: list[
        int
    ]  # if i is an index of tex_code, then find_line[i] is its column number
    tex_cleaned: str  # cleaned version of the TeX document (e.g. consecutive spaces are removed)
    pointer: list[
        None | int
    ]  # if j is an index of tex_cleaned, pointer[i] is the corresponding index in tex_code
    length: int  # length of tex_cleaned
    position: int  # current position in the document
    position_lock: bool  # prohibits the position to be changed
    document_lock: bool  # prohibits the document to be changed
    position_next: int  # next position (will become current position after calling apply_change())
    tex_code_next: str  # next TeX document (will become current document after calling apply_change())

    def __init__(self, tex_code: str) -> None:
        self.tex_code: str = tex_code
        self.__update_col_line()
        self.__clean()
        self.tex_code_next: str = tex_code
        self.position = self.position_next = 0
        self.position_lock = False
        self.document_lock = False

    def __update_col_line(self) -> None:
        """
        Compute two arrays, saying for each index i of self.text, at what column and
        what line of the text this index is located.
        """
        self.lines: list[str] = self.tex_code.split("\n")
        self.find_line: list[int] = [0] * len(self.tex_code)
        self.find_col: list[int] = [0] * len(self.tex_code)
        line: int = 1
        col: int = 1
        for position, letter in enumerate(self.tex_code):
            self.find_line[position] = line
            self.find_col[position] = col
            if letter == "\n":
                line += 1
                col = 1
            else:
                col += 1

    def __clean(self):
        """
        Reads self.tex_code (the original tex file), given as a single string.
        Converts spaces, tabulations and new lines into a single space, except
        if there is two consecutive new lines. Removes commented lines.
        The cleaned file is stored in self.tex_cleaned. A pointer
        from tex_cleaned to tex_code, in the form of an array, is produced in self.pointer.
        """

        # Essentially, the algorithm is a deterministic transducer with five states
        # 0: the last character is `normal` (not a space, a tab, nor a new line) ; initial state
        # 1: the last character is not normal,
        #   and no new line was read since the last normal character
        # 2: the last character is not normal,
        #   and exactly one new line was read since the last normal character
        # 3: the last character is not normal,
        #   and at least two new lines were read since the last normal character
        # 4: the line is commented.
        def is_normal(letter: str) -> bool:
            return letter not in [" ", "\t", "\n", "%"]

        def transition(
            state: int, letter: str, counter: int
        ) -> tuple[int, str, int | None]:
            """
            Input: curent state, input letter and the size of produced output so far
            Output: returns the new state, the output, and the pointer of the input letter.
            """
            if is_normal(letter):
                if state == 4:
                    return (4, "", None)
                return (0, letter, counter)
            if letter == "%":
                return (4, "", None)
            if letter == "\n":
                if state == 4:
                    return (0, "", None)
                if state == 0:
                    return (2, " ", None)
                if state == 1:
                    return (2, "", None)
                if state == 2:
                    return (3, "\n\n", counter)
                return (3, "", None)
            if letter in [" ", "\t"]:
                if state == 0:
                    return (1, " ", counter)
                return (state, "", None)
            raise KeyError("Transition not defined", state, letter)

        state: int = 0
        tex_cleaned: str = ""
        m: int = 0
        pointer: list[None | int] = []
        for position, letter in enumerate(self.tex_code):
            state, output, input_pointer = transition(state, letter, m)
            tex_cleaned += output
            m += len(output)
            # Put position at index input_pointer
            if input_pointer is not None:
                pointer += [None] * (input_pointer - len(pointer)) + [position]
        self.tex_cleaned: str = tex_cleaned
        self.pointer: list[None | int] = pointer
        self.length: int = len(self.tex_cleaned)

    def print(self, start: int, end: int, nb_lines: int, out: TextIO):
        """
        Prints the lines between positions (in the clean tex) `start` and `end`
        together with `nb_lines`-1 lines preceding `start`.
        Emphasize the part between `start` and `end`.
        """
        start_p = self.pointer[start]
        end_p = self.pointer[end]
        if isinstance(start_p, int) and isinstance(end_p, int):
            l_start: int = self.find_line[start_p]
            c_start: int = self.find_col[start_p]
            l_end: int = self.find_line[end_p]
            c_end: int = self.find_col[end_p]
            for i in range(max(0, l_start - nb_lines), l_end):
                if i + 1 == l_start and i + 1 == l_end:
                    print(
                        f"l{i+1}: \t{self.lines[i][:c_start-1]}"
                        + misc.emph(self.lines[i][c_start - 1 : c_end])
                        + self.lines[i][c_end:],
                        file=out,
                    )
                elif i + 1 == l_start:
                    print(
                        f"l{i+1}: \t{self.lines[i][:c_start-1]}"
                        + misc.emph(self.lines[i][c_start - 1 :]),
                        file=out,
                    )
                elif i + 1 == l_end:
                    print(
                        f"l{i+1}: \t"
                        + misc.emph(self.lines[i][:c_end])
                        + self.lines[i][c_end:],
                        file=out,
                    )
                elif l_start < i + 1 and i + 1 < l_end:
                    print(f"l{i+1}: \t" + misc.emph(self.lines[i]), file=out)
                else:
                    print(f"l{i+1}: \t{self.lines[i]}", file=out)
        else:
            raise IndexError("Undefined pointer", self.pointer, (start, end))

    def has_chars(self, length=1, start=0) -> bool:
        """Check if the cleaned document has at least `len` next characters."""
        return self.position + start + length <= self.length

    def get_chars(self, length=1, start=0) -> str:
        """Returns the current character of the cleaned document."""
        assert self.has_chars(length, start)
        return self.tex_cleaned[self.position + start : self.position + start + length]

    def get_control_sequence(self) -> str | None:
        """If the current position in the document is the beginning of a LaTeX control sequence,
        returns its name. Otheriwse, returns None."""
        if not self.has_chars():
            raise EOFError("Expected a control sequence.")
        if self.get_chars() != "\\":
            return None
        if not self.get_chars(start=1).isalpha():
            # Handles CS like \+ or \?
            return self.get_chars(start=1)
        length = 0
        while (
            self.has_chars(start=1 + length)
            and self.get_chars(start=1 + length).isalpha()
        ):
            length += 1
        return self.get_chars(length=length, start=1)

    def get_argument(self) -> str:
        """Parses a LaTeX argument in the document.
        On '{abc{def}foo[gh{f}]}lorem ipsum', returns 'abc{def}foo[gh{f}]',
        but on 'abc{def}foo[gh{f}]}lorem ipsum', returns 'a'."""
        if not self.has_chars():
            raise EOFError("Expected an argument.")
        if self.get_chars() != "{":
            return self.get_chars()
        nb_braces = 1
        pos = 1
        while nb_braces > 0:
            if not self.has_chars(start=pos):
                raise EOFError("EOF reached while parsing an argument.")
            match self.get_chars(start=pos):
                case "{":
                    nb_braces += 1
                case "}":
                    nb_braces -= 1
                case _:
                    ...
            pos += 1
        return self.get_chars(length=pos - 2, start=1)

    def get_begin_environment(self) -> str | None:
        r"""If the current position in the document is the beginning of a LaTeX environment,
        returns its name. Otherwise, returns None. Treats \( and \[ as beginnings of
        environments, whose name is `math`."""
        if self.get_control_sequence() == "begin":
            self.position += len("\\begin")
            env = self.get_argument()
            self.position -= len("\\begin")
            return env
        if self.startswith(["\\(", "\\["]):
            return "math"
        return None

    def get_end_environment(self) -> str | None:
        r"""If the current position in the document is the end of a LaTeX environment,
        returns its name. Otherwise, returns None. Treats \) and \] as ends of
        environments, whose name is `math`."""
        if self.get_control_sequence() == "end":
            self.position += len("\\end")
            env = self.get_argument()
            self.position -= len("\\end")
            return env
        if self.startswith(["\\)", "\\]"]):
            return "math"
        return None

    def startswith(self, strings: list[str]) -> list[str]:
        """Given a list of strings, returns the sublist of these strings
        that can be found at the beginning of the document (starting from the
        current position)."""
        # Todo (if necessary): improve using prefix tree.
        return [s for s in strings if self.tex_cleaned.startswith(s, self.position)]

    def increment_position(self, delta: int) -> bool:
        """Adds `delta` to the current position in the document.
        Returns a boolean, saying if the operation was succesful."""
        if not self.position_lock:
            self.position_lock = True
            self.position_next = self.position + delta
            return True
        return False

    def change_string(self, before: str, after: str) -> bool:
        """In the document, at the current position, changes the string `before`
        into `after`. Returns a boolean, saying if the operation was succesful."""
        assert self.startswith([before])
        if not self.document_lock:
            self.document_lock = True
            beg_original = self.pointer[self.position]
            assert beg_original is not None
            end = self.position + len(before)
            while end < self.length and self.pointer[end] is None:
                end += 1
            end_original = self.pointer[end] if end < self.length else len(self.tex_code)
            # the interval [beg_original, end_original[ corresponds to,
            # in tex_doc, to the string `before`.
            self.tex_code_next = (
                self.tex_code[:beg_original] + after + self.tex_code[end_original:]
            )
            return True
        return False

    def apply_change(self) -> None:
        self.tex_code = self.tex_code_next
        self.position = self.position_next
        self.__update_col_line()
        self.__clean()

    def reset_locks(self) -> None:
        """Resets the locks on the position and on the document."""
        self.position_lock = False
        self.document_lock = False

    def get_document_code(self) -> str:
        """Returns the TeX code of the document."""
        self.apply_change()
        return self.tex_code
