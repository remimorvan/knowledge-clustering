from __future__ import annotations

import copy

from knowledge_clustering import distance
from knowledge_clustering.knowledges import Knowledges


def clustering(
    knowledges: Knowledges,
    unknown_knowledges: list[str],
    alpha: float,
    list_prefixes: list[str],
    scopes_meaning: dict[str, list[list[str]]],
    lang: str,
):
    """
    Takes knowledges (object of type Knowledges), a list of unknown knowledges, a
    positive float `alpha` (threshold value for the clustering algorithm), a list
    of prefixes to ignore, a list of possible meanings for each scope, and a language id.
    Modifies the object knowledges so that it satisfies the following invariant:
    # any two notions in the same bag are near, where near either means:
    # - both in the same bag of knowledges at the beggining of the algorithm ;
    # - at distance (from module "dist") at most alpha if at least one of the two notions initially belongs to unknown_knowledges.
    """
    knowledges_processed_old = []
    knowledges_processed_new = knowledges.get_all_knowledges()
    while unknown_knowledges:
        # If there is no newly processed knowledge, pick an unknown knowledge and add it to a new bag.
        if not knowledges_processed_new:
            kl = unknown_knowledges[0]
            unknown_knowledges = unknown_knowledges[1:]
            knowledges.add_new_bag(kl)
            knowledges_processed_new = [kl]
        size_knowledges_processed_new = len(knowledges_processed_new)
        # Tries to add every unknown knowledge to a bag
        unknown_knowledges_copy = copy.copy(unknown_knowledges)
        for kl in unknown_knowledges_copy:
            dist_min = None
            kl2_min_list = []
            # Finds the processed notion that is at a minimal distance from kl
            for kl2 in knowledges_processed_new:
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
                knowledges.define_synonym_of(kl, kl2_min)
                unknown_knowledges.remove(kl)
                knowledges_processed_new.append(kl)
        # Every "new processed knowledge" that was known at the beginning of the while iteration
        # becomes an "old processed knowledge"
        knowledges_processed_old += knowledges_processed_new[
            :size_knowledges_processed_new
        ]
        knowledges_processed_new = knowledges_processed_new[
            size_knowledges_processed_new:
        ]
