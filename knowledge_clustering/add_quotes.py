import re  # Regular expressions
import knowledge_clustering.tex_code as tex

KL_DELIMITERS = [
    ('"', '"'),
    ("@", '"'),
    ("@", "@"),
    ("\kl{", "}"),
    ("\intro{", "}"),
    ("\\reintro{", "}"),
    ("\kl[", "]"),
    ("\intro[", "]"),
    ("\\reintro[", "]"),
]


def emph(str):
    return tex.BEGIN_EMPH + str + tex.END_EMPH


def emph_alt(str):
    return tex.BEGIN_EMPH_ALT + str + tex.END_EMPH


def ask_consent(message):
    ans = input(message)
    return ans.lower() in ["y", "yes"]


def add_quote(tex_code, add_quote_position, print_line, size_tab):
    """
    Given a tex code, and a list of triples (_, start, end), add a quote before the
    start and after the end. If the boolean interactive if true, asks the user
    if she wants to add quotes: moreover, print the print_line lines preceding
    the match before asking the user's input.
    """
    result = ""
    new_knowledges = []
    ignore_synonym = []
    ignore_subknowledge = []
    add_quote_position.sort(key=lambda x: x[1][1])
    add_quote_position_new = []
    for type, info in add_quote_position:
        if type == "newkl":
            (small_kl, small_start, small_end, big_kl, big_start, big_end) = info
            if big_kl not in ignore_synonym:
                if big_kl not in [k for (_, k) in new_knowledges]:
                    # Propose to the user to define a synonym
                    tex_code.print(
                        tex_code.find_line[big_start],
                        tex_code.find_col[big_start],
                        tex_code.find_line[big_end],
                        tex_code.find_col[big_end],
                        print_line,
                    )
                    message = f"Do you want to add `{emph_alt(big_kl)}` as a synonym of `{emph_alt(small_kl)}` and add quotes? [y/n] "
                    if ask_consent(message):
                        new_knowledges.append((small_kl, big_kl))
                        add_quote_position_new.append((big_kl, big_start, big_end))
                    else:
                        ignore_synonym.append(big_kl)
                        if small_kl == tex_code.tex_code[small_start : small_end + 1]:
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
            tex_code.print(
                tex_code.find_line[start],
                tex_code.find_col[start],
                tex_code.find_line[end],
                tex_code.find_col[end],
                print_line,
            )
            if ask_consent("Add quotes? [y/n] "):
                add_quote_position_new.append((kl, start, end))
            print("")
    add_quote_position = add_quote_position_new
    add_quote_before = [i for (_, i, _) in add_quote_position]
    add_quote_after = [j for (_, _, j) in add_quote_position]
    for i in range(len(tex_code.tex_code)):
        if i in add_quote_before:
            result += '"'
        result += tex_code.tex_code[i]
        if i in add_quote_after:
            result += '"'
    print(
        f"Added {len(add_quote_position)} pair"
        + ("s" if len(add_quote_position) > 1 else "")
        + f" of quotes. Defined {len(new_knowledges)} synonym"
        + ("s." if len(new_knowledges) > 1 else ".")
    )
    return result, new_knowledges


def quote_maximal_substrings(text, kl, print_line, size_tab=4):
    """
    Given a text (tex code), and a list of strings, returns the same text with quotes around maximal substrings. Arguments:
    - text: tex code
    - kl: structure containing (both known and new) knowledges
    - interactive: boolean; ask the user before adding quotes
    - suggest_kl: boolean; suggest to define new knowledges to the user
    - size_tab: number of columns taken by a tab
    Ex: on the text 'every ordered monoid is a monoid' with list_strings =
    ['monoid', 'ordered monoid'], returns
    'every "ordered monoid" is a "monoid"'.
    """

    def stop_expanding(char):
        return not char.isalpha()

    tex_code = tex.TexCode(text)
    tex_code.clean_text()

    ignore_position = [False] * len(tex_code.tex_cleaned)
    add_quote_location = []  # Triple (string, start, end)
    for ignore_case in [False, True]:
        # Start the algo by being case sensitive, then run it while being insensitive.
        for s1 in kl.all_knowledges_sorted:
            match_list = (
                re.finditer(re.escape(s1), tex_code.tex_cleaned, re.IGNORECASE)
                if ignore_case
                else re.finditer(re.escape(s1), tex_code.tex_cleaned)
            )
            for match in match_list:
                start, end = match.start(), match.end() - 1
                if not ignore_position[start]:
                    # Ignore every infix of s1 that is also a substring of the list
                    for i in range(start, end + 1):
                        ignore_position[i] = True
                    for s2 in kl.dependency[s1]:
                        for submatch in re.finditer(
                            re.escape(s2), tex_code.tex_cleaned[start : end + 1]
                        ):
                            ignore_position[start + submatch.start()] = True
                    # Check if s1 is precedeed by quotes, if not, either check
                    # if we can define a new knowledge, or add the match to the
                    # list of quotes to add.
                    if not True in [
                        tex_code.tex_cleaned.endswith(beg_kl, 0, start)
                        and tex_code.tex_cleaned.startswith(end_kl, end + 1)
                        for (beg_kl, end_kl) in KL_DELIMITERS
                    ]:
                        start2, end2 = start, end
                        while start2 > 0 and not stop_expanding(
                            tex_code.tex_cleaned[start2 - 1]
                        ):
                            start2 -= 1
                        while end2 + 1 < len(
                            tex_code.tex_cleaned
                        ) and not stop_expanding(tex_code.tex_cleaned[end2 + 1]):
                            end2 += 1
                        # text_cleaned[start2: end2 + 1] is the maximal substring
                        # containing text_cleaned[start, end + 1] = s1 as a factor,
                        # and obtained by only addings letters (no space).
                        new_kl = tex_code.tex_cleaned[start2 : end2 + 1]
                        if s1 != new_kl:
                            # Propose to add new_kl as a new knowledge
                            add_quote_location.append(
                                (
                                    "newkl",
                                    (
                                        s1,
                                        tex_code.pointer[start],
                                        tex_code.pointer[end],
                                        new_kl,
                                        tex_code.pointer[start2],
                                        tex_code.pointer[end2],
                                    ),
                                )
                            )
                        else:
                            add_quote_location.append(
                                (
                                    "addquote",
                                    (
                                        s1,
                                        tex_code.pointer[start],
                                        tex_code.pointer[end],
                                    ),
                                )
                            )
    return add_quote(tex_code, add_quote_location, print_line, size_tab)
