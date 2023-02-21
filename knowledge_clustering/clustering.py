"""Clustering algorithm."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

import copy

from knowledge_clustering import distance
from knowledge_clustering.knowledges import Knowledges


def clustering(
    kls: Knowledges,
    unknown_kl: list[str],
    alpha: float,
    list_prefixes: list[str],
    scopes_meaning: dict[str, list[list[str]]],
    lang: str,
):
    """
    Adds all knowledges in unknown_kl to the structure kls.

    The invariant satisfied by the algorithm is the following:
        any two notions in the same bag are near, where near either means:
            - both in the same bag of knowledges at the beggining of the algorithm ;
            - at distance (from module "dist") at most alpha if at least one of
                the two notions initially belongs to unknown_kls.

    Args:
        kl: known knowledges.
        unknown_kl: a list of unknown knowledges.
        alpha: a threshold indicating the maximal distance allowed for clustering
            two knowkledges together.
        list_prefixes: a list of prefixes that are ignored when computing the
            distance between two knowledges.
        scope_meaning: a dictionnary, assigning to every scope a list of
            its possible meanings, each possible meaning being a list of words;
            used to compute the distance.
        lang: a string describing the language of the document;
            a value from the dictionnary knowledge_clustering.app._NLTK_LANG;
            used to compute the distance.
    """
    kl_processed_old = []
    kl_processed_new = kls.get_all_knowledges()
    while unknown_kl:
        # If there is no newly processed knowledge, pick an unknown knowledge
        # and add it to a new bag.
        if not kl_processed_new:
            kl = unknown_kl[0]
            unknown_kl = unknown_kl[1:]
            kls.add_new_bag(kl)
            kl_processed_new = [kl]
        size_kl_processed_new = len(kl_processed_new)
        # Tries to add every unknown knowledge to a bag
        unknown_kl_copy = copy.copy(unknown_kl)
        for kl in unknown_kl_copy:
            dist_min = None
            kl2_min_list = []
            # Finds the processed notion that is at a minimal distance from kl
            for kl2 in kl_processed_new:
                d = distance.distance(kl, kl2, list_prefixes, scopes_meaning, lang)
                if dist_min is None or d < dist_min:
                    dist_min = d
                    kl2_min_list = [kl2]
                elif d == dist_min:
                    kl2_min_list.append(kl2)
            # If this minimal distance is smaller than the threshold alpha, add kl to the bag
            if dist_min is not None and dist_min <= alpha:
                # Choose kl2_min in kl2_min_list minimising the edit distance
                kl2_min = distance.minimise_levenshtein_distance(kl, kl2_min_list)
                # Add kl to the bag of kl2_min
                kls.define_synonym_of(kl, kl2_min)
                unknown_kl.remove(kl)
                kl_processed_new.append(kl)
        # Every "new processed knowledge" that was known at the beginning of the while iteration
        # becomes an "old processed knowledge"
        kl_processed_old += kl_processed_new[:size_kl_processed_new]
        kl_processed_new = kl_processed_new[size_kl_processed_new:]
