"""Infer the scope from known knowledges."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9
from typing import TypeVar

import copy

import knowledge_clustering.distance as dist

T = TypeVar("T")  # Generic type


def union_list_of_lists(l1: list[T], l2: list[T]) -> list[T]:
    """Returns the union (without repetition) of two lists of lists."""
    s = copy.copy(l1)
    for sublist in l2:
        if sublist not in s:
            s.append(sublist)
    return s


def infer_scope(list_kl: list[str], scope: str, lang: str, stemmer) -> list[list[str]]:
    """
    Takes a list of knowledges that all belong to the same bag and a scope.

    If the list contains a knowledge with this scope, we try to infer the meaning of the scope
    by looking at similar knowledges.

    Example:
        Running the algorithm on ["word@some-scope", "countable ordinal word",
        "ordinal word", "scattered language"] for the scope `some-scope` will return
        the list [["countable", "ordinal"], ["ordinal"]].
    """
    result: list[list[str]] = []
    list_kl_broke: list[tuple[list[str], str]] = [
        dist.breakup_notion(kl, lang) for kl in list_kl
    ]
    for kl1_words, sc1 in list_kl_broke:
        if sc1 == scope:
            for kl2_words, sc2 in list_kl_broke:
                if sc2 == "":
                    if dist.inclusion_sets_of_words(
                        kl1_words, kl2_words, [""], stemmer
                    ):
                        # If every word of kl1 appears in kl2 and kl2 has an empty scope,
                        # return the words in kl2 not appearing in kl1
                        result.append([w for w in kl2_words if w not in kl1_words])
    return result


def infer_all_scopes(
    known_knowledges: list[list[str]], lang: str
) -> dict[str, list[list[str]]]:
    """
    Given known knowledges and a langage, returns the infer meaning of scopes occuring
    in said these knowledges.
    """
    list_scopes: set[str] = {
        sc for bag in known_knowledges for (_, sc) in map(dist.extract_scope, bag)
    }
    if "" in list_scopes:
        list_scopes.remove("")
    scopes_meaning: dict[str, list[list[str]]] = {sc: [] for sc in list_scopes}
    stemmer = dist.new_stemmer(lang)
    for scope in list_scopes:
        for bag in known_knowledges:
            scopes_meaning[scope] = union_list_of_lists(
                scopes_meaning[scope], infer_scope(bag, scope, lang, stemmer)
            )
        if [scope] not in scopes_meaning[scope]:
            scopes_meaning[scope].append([scope])
    return scopes_meaning


def print_scopes(
    scopes_meaning: dict[str, list[list[str]]], print_meaning: bool = False
) -> None:
    """Prints the infered meaning of scopes."""
    print("Defined scopes:")
    if not print_meaning:
        print("\t", list(scopes_meaning.keys()))
    else:
        for sc in scopes_meaning:
            print(f"\t@{sc}:{scopes_meaning[sc]}")
