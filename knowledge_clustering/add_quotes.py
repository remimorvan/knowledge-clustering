import toposort  # Topological sort
import re  # Regular expressions


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


def add_quote(text, add_quote_position, interactive, print_col, size_tab):
    """
    Given a text, and a list of triples (_, start, end), add a quote before the start
    and after the end. If the boolean interactive if true, asks the user if she wants to
    add quotes.
    """
    result = ""
    if interactive:
        at_what_line, at_what_col = compute_line_col(text, size_tab)
        add_quote_position.sort(key=lambda x: x[1])
        add_quote_position_new = []
        for (kl, start, end) in add_quote_position:
            if print_col:
                message = f"Found a match for `{kl}` between line {at_what_line[start]}, \
column {at_what_col[start]} and line {at_what_line[end]}, column {at_what_col[end]}."
            else:
                if at_what_line[start] == at_what_line[end]:
                    message = f"Found a match for `{kl}` at line {at_what_line[start]}."
                else:
                    message = f"Found a match for `{kl}` between lines {at_what_line[start]} \
and {at_what_line[end]}."
            print(message)
            add = input("Add quotes? [y/n] ")
            if add.lower() in ["y", "yes"]:
                add_quote_position_new.append((kl, start, end))
        add_quote_position = add_quote_position_new
    add_quote_before = [i for (_, i, _) in add_quote_position]
    add_quote_after = [j for (_, _, j) in add_quote_position]
    for i in range(len(text)):
        if i in add_quote_before:
            result += '"'
        result += text[i]
        if i in add_quote_after:
            result += '"'
    print(f"Added {len(add_quote_position)} pairs of quotes.")
    return result


def ignore_spaces(tex_code):
    """
    Input: a tex file, given as a single string
    TeX converts spaces, tabulations and new lines into a single space, expect if there
    is two consecutive new lines.
    Output: we output the converted tex file, named tex_code_cleaned, and pointer
    from tex_code_cleaned to tex_code, in the form of an array.
    """
    # Essentially, the algorithm is a deterministic transducer with four states
    # 0: the last character is `normal` (not a space, a tab, nor a new line) ; initial state
    # 1: the last character is not normal, and no new line was read since the last normal character
    # 2: the last character is not normal, and exactly one new line was read since the last normal character
    # 3: the last character is not normal, and at least two new lines were read since the last normal character
    def is_normal(letter):
        return letter not in [" ", "\t", "\n"]

    def transition(state, letter, counter):
        """
        Input: curent state, input letter and the size of produced output so far
        Output: returns the new state, the output, and the pointer of the input letter.
        """
        if is_normal(letter):
            return (0, letter, counter)
        if letter == "\n":
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


def quote_maximal_substrings(
    text, list_strings, interactive=True, print_col=False, size_tab=4
):
    """
    Given a text (tex code), and a list of strings, returns the same text with quotes around maximal substrings.
    Ex: for the text 'every ordered monoid is a monoid' with list_strings = ['monoid', 'ordered monoid'],
    returns 'every "ordered monoid" is a "monoid"'.
    """
    text_cleaned, pointer = ignore_spaces(text)
    list_strings_sorted, dependency = topological_sort_string(list_strings)
    ignore_position = [False] * len(text_cleaned)
    add_quote_location = []  # Triple (string, start, end)
    for s1 in list_strings_sorted:
        for match in re.finditer(re.escape(s1), text_cleaned):
            start, end = match.start(), match.end() - 1
            if not ignore_position[start]:
                # Ignore every infix of s1 that is also a substring of the list
                for s2 in dependency[s1]:
                    for submatch in re.finditer(
                        re.escape(s2), text_cleaned[start : end + 1]
                    ):
                        ignore_position[start + submatch.start()] = True
                # Check if s1 is precedeed by quoted, if not add them
                if (
                    start > 0
                    and text_cleaned[start - 1] != '"'
                    and end < len(text_cleaned) - 1
                    and text_cleaned[end + 1] != '"'
                ):
                    add_quote_location.append((s1, start, end))
    # Using the pointer, describe where to add quotes in the original text
    add_quote_location_origin = [
        (s, pointer[i], pointer[j]) for (s, i, j) in add_quote_location
    ]
    if None in [i for (_, i, _) in add_quote_location_origin] + [
        j for (_, _, j) in add_quote_location_origin
    ]:
        print("Something went wrong. Maybe a knowledge starting or ending by a space?")
        exit(1)
    return add_quote(text, add_quote_location_origin, interactive, print_col, size_tab)
