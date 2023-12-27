"""
Adding anchor points to a document.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

import re  # Regular expressions
from typing import TextIO
import sys

from knowledge_clustering.tex_document import TexDocument
from knowledge_clustering import misc, cst


def app(tex_filename: str, space: int, out: TextIO = sys.stdout) -> None:
    """
    Prints warning when a knowledge is introduced but is not preceded by an anchor point.
    Args:
        tex_filename: the name of the tex file.
        space: an integer specifying the maximal number of characters allowed between the
            introduction of a knowledge and an anchor point.
        out: an output stream.
    """
    with open(tex_filename, "r", encoding="utf-8") as f:
        tex_doc = TexDocument(f.read())
    return missing_anchor(tex_doc, space, out)


def missing_anchor(tex_doc: TexDocument, space: int, out: TextIO) -> None:
    """
    Prints line numbers containing the introduction of a knowledge which
    is further away from an anchor point than the integer given as input.

    Args:
        tex_doc: a TeX document.
        space: the maximal distance between the introduction of a
            knowledge and the anchor point preceeding it.
        out: an output stream.
    """
    # First, compute the list of pairs (i1,i2,i3,i4) corresponding to
    # the indices in s = tex_doc.tex_cleaned of some pair in cst.INTRO_DELIMITERS, i.e.
    # (s[i1:i2], s[i3:i4]) is in cst.INTRO_DELIMITERS
    matches: list[tuple[int, int, int, int]] = []
    is_end_of_match = [False for _ in range(len(tex_doc.tex_cleaned))]
    for beg_str, end_str in cst.INTRO_DELIMITERS:
        for i_match in re.finditer(re.escape(beg_str), tex_doc.tex_cleaned):
            i1: int = i_match.start()
            i2: int = i_match.end()
            if not is_end_of_match[i1]:
                i3: int = i2 + tex_doc.tex_cleaned[i2:].find(end_str)
                i4: int = i3 + len(end_str)
                if i3 != -1:
                    matches.append((i1, i2, i3, i4))
                    is_end_of_match[i3] = True
    matches.sort(key=lambda x: x[0])
    for i1, i2, i3, _ in matches:
        beg: int = max(0, i1 - space)
        if not any(ap_str in tex_doc.tex_cleaned[beg:i1] for ap_str in cst.AP_STRING):
            start_pt: int | None = tex_doc.pointer[i1]
            if start_pt is not None:
                message: str = f"Missing anchor point at line {tex_doc.find_line[start_pt]} (knowledge: {misc.emph(tex_doc.tex_cleaned[i2:i3])})."
                print(message, file=out)
            else:
                raise Exception("Undefined pointer", tex_doc.pointer, i1)
