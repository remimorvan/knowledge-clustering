import toposort  # Topological sort
import re  # Regular expressions

KL_DELIMITERS = [
    ('"', '"'),
    ("@", '"'),
    ("@", "@"),
    ("\kl{", "}"),
    ("\intro{", "}"),
    ("\kl[", "]"),
    ("\intro[", "]"),
]

BEGIN_EMPH = "\033[1m\033[95m"
BEGIN_EMPH_NEW = "\033[1m\033[92m"
END_EMPH = "\033[0m"


def emph(str):
    return BEGIN_EMPH + str + END_EMPH


def emph_new(str):
    return BEGIN_EMPH_NEW + str + END_EMPH


def topological_sort_string(list_strings):
    """
    From a list of strings, computes a dependency graph whose vertices are strings of the input,
    with an edge from s1 to s2 if s2 is a substring of s1. Returns the list
    sorted according to a topological sort consistent with the dependency graph,
    and the dependency graph.
    """
    dependency = dict()
    dependency_reversed = dict()
    for s1 in list_strings:
        dependency[s1] = set([s2 for s2 in list_strings if s2 in s1 and s1 != s2])
        dependency_reversed[s1] = set(
            [s2 for s2 in list_strings if s1 in s2 and s1 != s2]
        )
    list_strings_sorted = list(toposort.toposort_flatten(dependency_reversed))
    return list_strings_sorted, dependency


def ask_consent(message):
    ans = input(message)
    return ans.lower() in ["y", "yes"]


def compute_line_col(text, size_tab):
    """Computes the line and column in which each letter of text is located."""
    at_what_line = [0] * len(text)
    at_what_col = [0] * len(text)
    line = 1
    col = 1
    for (position, letter) in enumerate(text):
        at_what_line[position] = line
        at_what_col[position] = col
        if letter == "\n":
            line += 1
            col = 1
        if letter == "\t":
            col += size_tab
        else:
            col += 1
    return at_what_line, at_what_col


def print_lines(text_lines, l_start, c_start, l_end, c_end, n):
    """Prints $n$ lines preceding the l_start-th line (included),
    and lines from l_start to l_end. Emphasize the part between column c_start and c_end"""
    for i in range(max(0, l_start - n), l_end):
        if i + 1 == l_start and i + 1 == l_end:
            print(
                f"l{i+1}: \t{text_lines[i][:c_start-2]}"
                + BEGIN_EMPH
                + text_lines[i][c_start - 2 : c_end - 1]
                + END_EMPH
                + text_lines[i][c_end - 1 :]
            )
        elif i + 1 == l_start:
            print(
                f"l{i+1}: \t{text_lines[i][:c_start-2]}"
                + BEGIN_EMPH
                + text_lines[i][c_start - 2 :]
                + END_EMPH
            )
        elif i + 1 == l_end:
            print(
                f"l{i+1}: \t"
                + BEGIN_EMPH
                + text_lines[i][: c_end - 1]
                + END_EMPH
                + text_lines[i][c_end - 1 :]
            )
        elif l_start < i + 1 and i + 1 < l_end:
            print(f"l{i+1}: \t" + BEGIN_EMPH + text_lines[i] + END_EMPH)
        else:
            print(f"l{i+1}: \t{text_lines[i]}")


def add_quote(text, add_quote_position, print_line, size_tab):
    """
    Given a text, and a list of triples (_, start, end), add a quote before the
    start and after the end. If the boolean interactive if true, asks the user
    if she wants to add quotes: moreover, print the print_line lines preceding
    the match before asking the user's input.
    """
    result = ""
    new_knowledges = []
    ignore_synonym = []
    ignore_subknowledge = []
    at_what_line, at_what_col = compute_line_col(text, size_tab)
    add_quote_position.sort(key=lambda x: x[1][1])
    add_quote_position_new = []
    text_lines = text.split("\n")
    for type, info in add_quote_position:
        if type == "newkl":
            (small_kl, small_start, small_end, big_kl, big_start, big_end) = info
            if big_kl not in ignore_synonym:
                if big_kl not in [k for (_, k) in new_knowledges]:
                    # Propose to the user to define a synonym
                    print_lines(
                        text_lines,
                        at_what_line[big_start],
                        at_what_col[big_start],
                        at_what_line[big_end],
                        at_what_col[big_end],
                        print_line,
                    )
                    message = f"Do you want to add `{emph_new(big_kl)}` as a synonym of `{emph_new(small_kl)}` and add quotes? [y/n] "
                    if ask_consent(message):
                        new_knowledges.append((small_kl, big_kl))
                        add_quote_position_new.append((big_kl, big_start, big_end))
                    else:
                        ignore_synonym.append(big_kl)
                        if ask_consent(
                            f"Add quotes around `{emph(small_kl)}` instead? [y/n] "
                        ):
                            add_quote_position_new.append(
                                (small_kl, small_start, small_end)
                            )
                        else:
                            ignore_subknowledge.append(big_kl)
                    print("")
                else:
                    # If big_kl was already accepted as a synonym earlier, treat it
                    # as a regular knowledge
                    type, info = "addquote", (big_kl, big_start, big_end)
            elif big_kl not in ignore_subknowledge:
                # If the user doesn't want big_kl as a synonym but might want
                # to add quotes around small_kl
                type, info = "addquote", (small_kl, small_start, small_end)
        if type == "addquote":
            (kl, start, end) = info
            print_lines(
                text_lines,
                at_what_line[start],
                at_what_col[start],
                at_what_line[end],
                at_what_col[end],
                print_line,
            )
            if ask_consent("Add quotes? [y/n] "):
                add_quote_position_new.append((kl, start, end))
            print("")
    add_quote_position = add_quote_position_new
    add_quote_before = [i for (_, i, _) in add_quote_position]
    add_quote_after = [j for (_, _, j) in add_quote_position]
    for i in range(len(text)):
        if i in add_quote_before:
            result += '"'
        result += text[i]
        if i in add_quote_after:
            result += '"'
    print(
        f"Added {len(add_quote_position)} pair"
        + ("s" if len(add_quote_position) > 1 else "")
        + f" of quotes. Defined {len(new_knowledges)} synonym"
        + ("s." if len(new_knowledges) > 1 else ".")
    )
    return result, new_knowledges


def ignore_spaces(tex_code):
    """
    Input: a tex file, given as a single string
    TeX converts spaces, tabulations and new lines into a single space, except
    if there is two consecutive new lines.
    Removes commented lines.
    Output: we output the converted tex file, named tex_code_cleaned, and pointer
    from tex_code_cleaned to tex_code, in the form of an array.
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
    tex_code_cleaned = ""
    m = 0
    pointer = []
    for position, letter in enumerate(tex_code):
        state, output, input_pointer = transition(state, letter, m)
        tex_code_cleaned += output
        m += len(output)
        # Put position at index input_pointer
        if input_pointer != None:
            pointer += [None] * (input_pointer - len(pointer)) + [position]
    return tex_code_cleaned, pointer


def quote_maximal_substrings(text, list_strings, print_line, size_tab=4):
    """
    Given a text (tex code), and a list of strings, returns the same text with quotes around maximal substrings. Arguments:
    - text: tex code
    - list_strings: defined knowledges
    - interactive: boolean; ask the user before adding quotes
    - suggest_kl: boolean; suggest to define new knowledges to the user
    - size_tab: number of columns taken by a tab
    Ex: on the text 'every ordered monoid is a monoid' with list_strings =
    ['monoid', 'ordered monoid'], returns
    'every "ordered monoid" is a "monoid"'.
    """

    def stop_expanding(char):
        return not char.isalpha()

    text_cleaned, pointer = ignore_spaces(text)
    list_strings_sorted, dependency = topological_sort_string(list_strings)
    ignore_position = [False] * len(text_cleaned)
    add_quote_location = []  # Triple (string, start, end)
    for ignore_case in [False, True]:
        # Start the algo by being case sensitive, then run it while being insensitive.
        for s1 in list_strings_sorted:
            match_list = (
                re.finditer(re.escape(s1), text_cleaned, re.IGNORECASE)
                if ignore_case
                else re.finditer(re.escape(s1), text_cleaned)
            )
            for match in match_list:
                start, end = match.start(), match.end() - 1
                if not ignore_position[start]:
                    # Ignore every infix of s1 that is also a substring of the list
                    ignore_position[start] = True
                    for s2 in dependency[s1]:
                        for submatch in re.finditer(
                            re.escape(s2), text_cleaned[start : end + 1]
                        ):
                            ignore_position[start + submatch.start()] = True
                    # Check if s1 is precedeed by quotes, if not, either check
                    # if we can define a new knowledge, or add the match to the
                    # list of quotes to add.
                    if not True in [
                        text_cleaned.endswith(beg_kl, 0, start)
                        and text_cleaned.startswith(end_kl, end + 1)
                        for (beg_kl, end_kl) in KL_DELIMITERS
                    ]:
                        start2, end2 = start, end
                        while start2 > 0 and not stop_expanding(
                            text_cleaned[start2 - 1]
                        ):
                            start2 -= 1
                        while end2 + 1 < len(text_cleaned) and not stop_expanding(
                            text_cleaned[end2 + 1]
                        ):
                            end2 += 1
                        # text_cleaned[start2: end2 + 1] is the maximal substring
                        # containing text_cleaned[start, end + 1] = s1 as a factor,
                        # and obtained by only addings letters (no space).
                        new_kl = text_cleaned[start2 : end2 + 1]
                        if s1 != new_kl:
                            # Propose to add new_kl as a new knowledge
                            add_quote_location.append(
                                (
                                    "newkl",
                                    (
                                        s1,
                                        pointer[start],
                                        pointer[end],
                                        new_kl,
                                        pointer[start2],
                                        pointer[end2],
                                    ),
                                )
                            )
                        else:
                            add_quote_location.append(
                                ("addquote", (s1, pointer[start], pointer[end]))
                            )
    return add_quote(text, add_quote_location, print_line, size_tab)
