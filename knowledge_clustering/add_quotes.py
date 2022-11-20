from __future__ import annotations

import re  # Regular expressions
from typing import NamedTuple

from knowledge_clustering.knowledges import Knowledges
from knowledge_clustering.tex_document import TexDocument
from knowledge_clustering import misc

_KL_DELIMITERS = [
    ('"', '"'),
    ("@", '"'),
    ("@", "@"),
    ("\\kl{", "}"),
    ("\\intro{", "}"),
    ("\\reintro{", "}"),
    ("\\kl[", "]"),
    ("\\intro[", "]"),
    ("\\reintro[", "]"),
]


class NewKL(NamedTuple):
    kl_origin: str
    start_origin: int
    end_origin: int
    kl: str
    start: int
    end: int


class AddQuote(NamedTuple):
    kl: str
    start: int
    end: int


def ask_consent(message: str):
    """
    Asks whether the user wants to do an action, after printing the string `message`.
    Returns a boolean.
    """
    ans = input(message)
    return ans.lower() in ["y", "yes"]


def add_quote(
    tex_doc: TexDocument,
    operations: list[NewKL | AddQuote],
    print_line: int,
):
    """
    Args:
        tex_doc: a tex document
        add_quote_position:
        print_line:
    Given a tex code, and a list of triples (_, start, end), add a quote before the
    start and after the end. If the boolean interactive if true, asks the user
    if they want to add quotes: moreover, print the print_line lines preceding
    the match before asking the user's input.
    """
    result = ""
    new_knowledges = []
    ignore_synonym = []
    ignore_subknowledge = []
    operations.sort(key=lambda x: x.start)
    operations_addquote: list[AddQuote] = []
    for op in operations:
        if isinstance(op, NewKL):
            if op.kl not in ignore_synonym:
                if op.kl not in [k for (_, k) in new_knowledges]:
                    # Propose to the user to define a synonym
                    tex_doc.print(
                        op.start,
                        op.end,
                        print_line,
                    )
                    message = (
                        f"Do you want to add `{misc.emph_alt(op.kl)}` as a synonym "
                        f"of `{misc.emph_alt(op.kl_origin)}` and add quotes? [y/n] "
                    )
                    if ask_consent(message):
                        # Adds op.kl as a new knowledge, defined as a synonym of op.kl_origin
                        new_knowledges.append((op.kl_origin, op.kl))
                        operations_addquote.append(AddQuote(op.kl, op.start, op.end))
                        # Removes any operations occuring on a substring of our new knowledge
                        for op2 in operations:
                            if isinstance(op2, AddQuote):
                                if op.start <= op2.start and op2.end <= op.end:
                                    operations.remove(op2)
                    else:
                        # From this point, do not propose again to define op.kl as a new knowledge.
                        ignore_synonym.append(op.kl)
                        if (
                            op.kl_origin
                            == tex_doc.tex_code[op.start_origin : op.end_origin + 1]
                        ):
                            # Propose to the user to add quotes around the original knowledge instead, if we have a precise match.
                            if ask_consent(
                                f"Add quotes around `{misc.emph(op.kl_origin)}` instead? [y/n] "
                            ):
                                operations_addquote.append(
                                    AddQuote(
                                        op.kl_origin, op.start_origin, op.end_origin
                                    )
                                )
                            else:
                                ignore_subknowledge.append(op.kl)
                    print("")
                else:
                    # If op.kl was already accepted as a synonym earlier, treat it
                    # as a regular knowledge
                    op = AddQuote(op.kl, op.start, op.end)
            elif op.kl not in ignore_subknowledge:
                # If the user doesn't want op.kl as a synonym but might want
                # to add quotes around op.kl_origin
                op = AddQuote(op.kl_origin, op.start_origin, op.end_origin)
        elif isinstance(op, AddQuote):
            tex_doc.print(
                op.start,
                op.end,
                print_line,
            )
            if ask_consent("Add quotes? [y/n] "):
                operations_addquote.append(op)
            print("")
    add_quote_before = [tex_doc.pointer[op.start] for op in operations_addquote]
    add_quote_after = [tex_doc.pointer[op.end] for op in operations_addquote]
    for i in range(len(tex_doc.tex_code)):
        if i in add_quote_before:
            result += '"'
        result += tex_doc.tex_code[i]
        if i in add_quote_after:
            result += '"'
    print(
        f"Added {len(operations_addquote)} pair"
        + ("s" if len(operations_addquote) > 1 else "")
        + f" of quotes. Defined {len(new_knowledges)} synonym"
        + ("s." if len(new_knowledges) > 1 else ".")
    )
    return result, new_knowledges


def quote_maximal_substrings(
    tex_doc: TexDocument, kl: Knowledges, print_line: int, size_tab: int = 4
):
    """
    Given a tex code and knowledges, returns the same text with quotes around maximal substrings
    that corresponds to knowledges. The integer `print_line` corresponds to the number
    of lines printed when asking the user if they want to add quotes.
    """

    def stop_expanding(char):
        return not char.isalpha()

    ignore_position = [False] * tex_doc.length
    add_quote_location: list[NewKL | AddQuote] = []
    for ignore_case in [False, True]:
        # Start the algo by being case sensitive, then run it while being insensitive.
        for s1 in kl.all_knowledges_sorted:
            match_list = (
                re.finditer(re.escape(s1), tex_doc.tex_cleaned, re.IGNORECASE)
                if ignore_case
                else re.finditer(re.escape(s1), tex_doc.tex_cleaned)
            )
            for match in match_list:
                start, end = match.start(), match.end() - 1
                if not ignore_position[start]:
                    # Ignore every infix of s1 that is also a substring of the list
                    for i in range(start, end + 1):
                        ignore_position[i] = True
                    for s2 in kl.dependency[s1]:
                        for submatch in re.finditer(
                            re.escape(s2), tex_doc.tex_cleaned[start : end + 1]
                        ):
                            ignore_position[start + submatch.start()] = True
                    # Check if s1 is precedeed by quotes, if not, either check
                    # if we can define a new knowledge, or add the match to the
                    # list of quotes to add.
                    if not any(
                        [
                            tex_doc.tex_cleaned.endswith(beg_kl, 0, start)
                            and tex_doc.tex_cleaned.startswith(end_kl, end + 1)
                            for (beg_kl, end_kl) in _KL_DELIMITERS
                        ]
                    ):
                        start2, end2 = start, end
                        while start2 > 0 and not stop_expanding(
                            tex_doc.tex_cleaned[start2 - 1]
                        ):
                            start2 -= 1
                        while end2 + 1 < len(
                            tex_doc.tex_cleaned
                        ) and not stop_expanding(tex_doc.tex_cleaned[end2 + 1]):
                            end2 += 1
                        # text_cleaned[start2: end2 + 1] is the maximal substring
                        # containing text_cleaned[start, end + 1] = s1 as a factor,
                        # and obtained by only addings letters (no space).
                        new_kl = tex_doc.tex_cleaned[start2 : end2 + 1]
                        if s1 != new_kl:
                            # Propose to add new_kl as a new knowledge
                            add_quote_location.append(
                                NewKL(s1, start, end, new_kl, start2, end2)
                            )
                        else:
                            add_quote_location.append(AddQuote(s1, start, end))
    return add_quote(tex_doc, add_quote_location, print_line)
