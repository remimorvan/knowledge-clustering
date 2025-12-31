from knowledge_clustering.tex_document import TexDocument


def test_document_read() -> None:
    """Tests methods related to parsing/reading the document."""
    doc = TexDocument(
        r"""This is a \emph{sample}  of a \LaTeX~document $\+A$ with \begin{center} environments! \end{center} and so on."""
    )
    doc.position = 10
    assert doc.has_chars()
    assert doc.get_chars() == "\\"
    assert doc.get_control_sequence() == "emph"
    doc.position = 14
    assert doc.get_argument() == "h"
    assert doc.get_begin_environment() == None
    assert doc.get_end_environment() == None
    doc.position = 15
    assert doc.get_argument() == "sample"
    doc.position = 46
    assert doc.get_control_sequence() == "+"
    assert doc.get_begin_environment() == None
    assert doc.get_end_environment() == None
    doc.position = 56
    assert doc.get_begin_environment() == "center"
    assert doc.get_end_environment() == None
    doc.position = 85
    assert doc.get_begin_environment() == None
    assert doc.get_end_environment() == "center"


def test_document_change() -> None:
    """Tests methods related to updating the document."""
    doc = TexDocument(
        r"""This is a \emph{sample}  of a \LaTeX~document $\+A$ with \begin{center} environments! \end{center} and so on."""
    )
    doc.position = 10
    tex_code_before = doc.tex_code
    tex_cleaned_before = doc.tex_cleaned
    new_string = r"sample of a {\LaTeX} document."
    assert doc.change_string(r"\emph{sample} of a \LaTeX~document", new_string)
    assert tex_code_before == doc.tex_code
    assert tex_cleaned_before == doc.tex_cleaned
    doc.apply_change()
    doc.position = 10
    assert tex_code_before != doc.tex_code
    assert doc.get_chars(length=len(new_string)) == new_string
