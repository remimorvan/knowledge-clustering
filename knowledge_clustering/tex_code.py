BEGIN_EMPH = "\033[1m\033[95m"
BEGIN_EMPH_ALT = "\033[1m\033[92m"
BEGIN_EMPH_BOLD = "\033[1m"
END_EMPH = "\033[0m"


class TexCode:
    def __init__(self, tex_code, size_tab=4):
        self.tex_code = tex_code
        self.lines = self.tex_code.split("\n")
        self.size_tab = size_tab
        self.__update_col_line()
        self.__clean()
        self.length = len(self.tex_cleaned)

    def __update_col_line(self):
        """
        Compute two arrays, saying for each index i of self.text, at what column and
        what line of the text this index is located.
        """
        self.find_line = [0] * len(self.tex_code)
        self.find_col = [0] * len(self.tex_code)
        line = 1
        col = 1
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
        # 1: the last character is not normal, and no new line was read since the last normal character
        # 2: the last character is not normal, and exactly one new line was read since the last normal character
        # 3: the last character is not normal, and at least two new lines were read since the last normal character
        # 4: the line is commented.
        def is_normal(letter):
            return letter not in [" ", "\t", "\n", "%"]

        def transition(state, letter, counter):
            """
            Input: curent state, input letter and the size of produced output so far
            Output: returns the new state, the output, and the pointer of the input letter.
            """
            if is_normal(letter):
                if state == 4:
                    return (4, "", None)
                else:
                    return (0, letter, counter)
            if letter == "%":
                return (4, "", None)
            if letter == "\n":
                if state == 4:
                    return (0, "", None)
                if state == 0:
                    return (2, " ", None)
                elif state == 1:
                    return (2, "", None)
                elif state == 2:
                    return (3, "\par ", counter)
                else:
                    return (3, "", None)
            if letter in [" ", "\t"]:
                if state == 0:
                    return (1, " ", counter)
                else:
                    return (state, "", None)

        state = 0
        tex_cleaned = ""
        m = 0
        pointer = []
        for position, letter in enumerate(self.tex_code):
            state, output, input_pointer = transition(state, letter, m)
            tex_cleaned += output
            m += len(output)
            # Put position at index input_pointer
            if input_pointer != None:
                pointer += [None] * (input_pointer - len(pointer)) + [position]
        self.tex_cleaned = tex_cleaned
        self.pointer = pointer

    def print(self, start, end, n):
        """
        Prints the lines between positions (in the clean tex) `start` and `end`
        together with `n`-1 lines preceding `start`.
        Emphasize the part between `start` and `end`.
        """
        l_start = self.find_line[self.pointer[start]]
        c_start = self.find_col[self.pointer[start]]
        l_end = self.find_line[self.pointer[end]]
        c_end = self.find_col[self.pointer[end]]
        for i in range(max(0, l_start - n), l_end):
            if i + 1 == l_start and i + 1 == l_end:
                print(
                    f"l{i+1}: \t{self.lines[i][:c_start-1]}"
                    + BEGIN_EMPH
                    + self.lines[i][c_start - 1 : c_end]
                    + END_EMPH
                    + self.lines[i][c_end:]
                )
            elif i + 1 == l_start:
                print(
                    f"l{i+1}: \t{self.lines[i][:c_start-1]}"
                    + BEGIN_EMPH
                    + self.lines[i][c_start - 1 :]
                    + END_EMPH
                )
            elif i + 1 == l_end:
                print(
                    f"l{i+1}: \t"
                    + BEGIN_EMPH
                    + self.lines[i][:c_end]
                    + END_EMPH
                    + self.lines[i][c_end:]
                )
            elif l_start < i + 1 and i + 1 < l_end:
                print(f"l{i+1}: \t" + BEGIN_EMPH + self.lines[i] + END_EMPH)
            else:
                print(f"l{i+1}: \t{self.lines[i]}")
