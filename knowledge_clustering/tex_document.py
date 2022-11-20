from __future__ import annotations

from knowledge_clustering import misc


class TexDocument:
    def __init__(self, tex_code: str, size_tab: int = 4) -> None:
        self.tex_code: str = tex_code
        self.lines: list[str] = self.tex_code.split("\n")
        self.size_tab: int = size_tab
        self.__update_col_line()
        self.__clean()
        self.length: int = len(self.tex_cleaned)

    def __update_col_line(self) -> None:
        """
        Compute two arrays, saying for each index i of self.text, at what column and
        what line of the text this index is located.
        """
        self.find_line: list[int] = [0] * len(self.tex_code)
        self.find_col: list[int] = [0] * len(self.tex_code)
        line: int = 1
        col: int = 1
        for (position, letter) in enumerate(self.tex_code):
            self.find_line[position] = line
            self.find_col[position] = col
            if letter == "\n":
                line += 1
                col = 0
            if letter == "\t":
                col += self.size_tab
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
                    return (3, "\\par ", counter)
                return (3, "", None)
            if letter in [" ", "\t"]:
                if state == 0:
                    return (1, " ", counter)
                return (state, "", None)
            raise Exception("Transition not defined", state, letter)

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

    def print(self, start: int, end: int, n: int):
        """
        Prints the lines between positions (in the clean tex) `start` and `end`
        together with `n`-1 lines preceding `start`.
        Emphasize the part between `start` and `end`.
        """
        start_p = self.pointer[start]
        end_p = self.pointer[end]
        if isinstance(start_p, int) and isinstance(end_p, int):
            l_start: int = self.find_line[start_p]
            c_start: int = self.find_col[start_p]
            l_end: int = self.find_line[end_p]
            c_end: int = self.find_col[end_p]
            for i in range(max(0, l_start - n), l_end):
                if i + 1 == l_start and i + 1 == l_end:
                    print(
                        f"l{i+1}: \t{self.lines[i][:c_start-1]}"
                        + misc.emph(self.lines[i][c_start - 1 : c_end])
                        + self.lines[i][c_end:]
                    )
                elif i + 1 == l_start:
                    print(
                        f"l{i+1}: \t{self.lines[i][:c_start-1]}"
                        + misc.emph(self.lines[i][c_start - 1 :])
                    )
                elif i + 1 == l_end:
                    print(
                        f"l{i+1}: \t"
                        + misc.emph(self.lines[i][:c_end])
                        + self.lines[i][c_end:]
                    )
                elif l_start < i + 1 and i + 1 < l_end:
                    print(f"l{i+1}: \t" + misc.emph(self.lines[i]))
                else:
                    print(f"l{i+1}: \t{self.lines[i]}")
        else:
            raise Exception("Undefined pointer", self.pointer, (start, end))
