from pylatexenc.latexwalker import LatexWalker
from pylatexenc.latexwalker import (
    LatexNode,
    LatexCharsNode,
    LatexGroupNode,
    LatexCommentNode,
    LatexMacroNode,
    LatexEnvironmentNode,
    LatexSpecialsNode,
    LatexMathNode,
)


def depth_first_search_list(nodes: list[LatexNode | None]) -> None:
    assert type(nodes) is list
    for node in nodes:
        depth_first_search_node(node)


def depth_first_search_node(node: LatexNode | None) -> None:
    if node is None:
        return
    assert isinstance(node, LatexNode)
    if node.isNodeType(LatexCharsNode):
        print(node.chars, end="")
    elif node.isNodeType(LatexGroupNode):
        depth_first_search_list(node.nodelist)
    elif node.isNodeType(LatexCommentNode):
        ...
    elif node.isNodeType(LatexMacroNode):
        depth_first_search_list(node.nodeargd.argnlist)
    elif node.isNodeType(LatexEnvironmentNode):
        depth_first_search_list(node.nodelist)
    elif node.isNodeType(LatexSpecialsNode):
        # Represents a special char like & or ~. Because of this, knowledges with '~' will
        # not be recognised unless the document is preprocessed.
        ...
    elif node.isNodeType(LatexMathNode):
        depth_first_search_list(node.nodelist)
    else:
        raise TypeError(f"Unknown type of LaTeX node ({node.nodeType()}).")
