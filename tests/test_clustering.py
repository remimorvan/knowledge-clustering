"""
Tests for the modules of knowledge_clustering on which the cluster command is based.
"""

from typing import TypeVar

from knowledge_clustering.distance import distance, new_stemmer
from knowledge_clustering.scope_meaning import infer_scope, infer_all_scopes
from knowledge_clustering.clustering import clustering
from knowledge_clustering.knowledges import Knowledges
from knowledge_clustering.diagnose import parse as parse_diagnose
from knowledge_clustering.config import parse as parse_config

T = TypeVar("T")  # Generic type


def test_distance() -> None:
    """Test functions from the the distance module."""
    # Tests where only the empty word is allowed as a prefix. No prior scope meaning is known.
    assert distance("ordinal semigroup", "ordinal semigroups", [""], {}, "english") == 0
    assert distance("cheval", "chevaux", [""], {}, "french") == 0
    assert distance("cheval", "chevaux", [""], {}, "english") > 0
    # Tests with a scope
    assert distance("ordinal semigroup", "semigroups@ordinal", [""], {}, "english") == 0
    assert distance("semigroup", "semigroups@ordinal", [""], {}, "english") > 0
    # Tests with prefixes
    assert distance("foo", "turbofoo", ["", "turbo"], {}, "english") == 0
    assert distance("foo", "turbofoo", [""], {}, "english") > 0
    assert distance("foo", "megafoo", ["", "turbo"], {}, "english") > 0
    # Test with accent and math
    assert distance("Büchi", 'B\\"uchi', [""], {}, "english") == 0
    assert (
        distance("Büchi", '\\textsf{$\\omega$-B\\"{u}chi}', ["", "-"], {}, "english")
        == 0
    )
    # Tests with scope
    assert (
        distance("word@ord", "ordinal word", [""], {"ord": [["ordinal"]]}, "english")
        == 0
    )
    assert distance("word@ord", "ordinal word", [""], {}, "english") > 0


def compare(l1: list[list[T]], l2: list[list[T]]) -> bool:
    """Compares if two lists of lists contain the same elements."""

    def compare_lists(t1: list[T], t2: list[T]) -> bool:
        return set(t1) == set(t2)

    for t1 in l1:
        if not any(compare_lists(t1, t2) for t2 in l2):
            return False
    for t2 in l2:
        if not any(compare_lists(t1, t2) for t1 in l1):
            return False
    return True


def test_scope_meaning() -> None:
    """Tests functions from the module scope_meaning"""
    # Test infer_scope
    assert compare(
        infer_scope(
            ["regular language over countable ordinals", "regular languages@ord"],
            "ord",
            "english",
            new_stemmer("english"),
        ),
        [["ordinals", "countable"]],
    )
    # Test infer_all_scopes
    assert compare(
        infer_all_scopes(
            [
                [
                    "word@some-scope",
                    "foo word",
                ],
                ["langage@some-scope", "bar langage"],
            ],
            "english",
        )["some-scope"],
        [["foo"], ["bar"], ["some-scope"]],
    )


def test_clustering() -> None:
    """Tests functions from the clustering module."""
    kls = Knowledges("examples/ordinal-kl.tex")
    unknown_kl = parse_diagnose("examples/ordinal.diagnose")
    list_prefixes = parse_config("knowledge_clustering/data/english.ini")
    scopes_meaning = infer_all_scopes(kls.get_all_bags(), "english")
    clustering(kls, unknown_kl, 0, list_prefixes, scopes_meaning, "english")
    solution = [
        ["word", "words"],
        ["word@ord", "countable ordinal word"],
        ["regular language over countable ordinals", "regular languages@ord"],
        ["separation", "inseparability"],
        ["semigroup", "semigroups"],
    ]
    assert compare(kls.get_all_bags(), solution)