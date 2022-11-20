from __future__ import annotations

from knowledge_clustering.tex_document import TexDocument
import re  # Regular expressions


_INTRO_STRING = ["\\intro", '""']
_AP_STRING = ["\\AP", "\\itemAP"]


def missing_AP(tex_doc: TexDocument, space: int) -> None:
    """
    Args:
        text: a string containing the code of a TeX document
        space: the maximal distance between the introduction of a
            knowledge and the anchor point preceeding it.
        size_tab:
    """
    for i_str in _INTRO_STRING:
        for i_match in re.finditer(re.escape(i_str), tex_doc.tex_cleaned):
            start = i_match.start()
            beg = max(0, start - space)
            if not any(
                [ap_str in tex_doc.tex_cleaned[beg:start] for ap_str in _AP_STRING]
            ):
                start_pt: int | None = tex_doc.pointer[start]
                if start_pt is not None:
                    message: str = (
                        f"Missing anchor point at line {tex_doc.find_line[start_pt]}."
                    )
                    print(message)
                else:
                    raise Exception("Undefined pointer", tex_doc.pointer, start)
