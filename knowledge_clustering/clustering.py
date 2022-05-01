import knowledge_clustering.distance as dist
import copy


def bagId(known_knowledges, kl):
    i = 0
    n = len(known_knowledges)
    while i < n and kl not in known_knowledges[i]:
        i += 1
    return i


def clustering(
    known_knowledges, unknown_knowledges, alpha, list_prefixes, scopes_meaning, lang
):
    # Takes a list of lists of known knowledges, a list of unknown knowledges, a threshold alpha (positive float)
    # and modifies known_knowledges and unknown_knowledges so that at the end every notion of unknown_knowledges
    # is moved to some bag of known_knowledges. The bags of known_knowledges satisfy the following invariant:
    # any two notions in the same bag are near, where near either means:
    # - both in the same bag of known_knowledges at the beggining of the algorithm ;
    # - at distance (from module "dist") at most alpha if at least one of the two notions initially belongs to unknown_knowledges.
    knowledges_processed_old = []
    knowledges_processed_new = [kl for bag in known_knowledges for kl in bag]
    while unknown_knowledges != []:
        # If there is no newly processed knowledge, pick an unknown knowledge and add it to a new bag.
        if knowledges_processed_new == []:
            kl = unknown_knowledges[0]
            unknown_knowledges = unknown_knowledges[1:]
            known_knowledges.append([kl])
            knowledges_processed_new = [kl]
        size_knowledges_processed_new = len(knowledges_processed_new)
        # Tries to add every unknown knowledge to a bag
        unknown_knowledges_copy = copy.copy(unknown_knowledges)
        for kl in unknown_knowledges_copy:
            dist_min = None
            kl2_min_list = []
            # Finds the processed notion that is at a minimal distance from kl
            for kl2 in knowledges_processed_new:
                d = dist.distance(kl, kl2, list_prefixes, scopes_meaning, lang)
                if dist_min == None or d < dist_min:
                    dist_min = d
                    kl2_min_list = [kl2]
                elif d == dist_min:
                    kl2_min_list.append(kl2)
            # If this minimal distance is smaller than the threshold alpha, add kl to the bag
            if dist_min <= alpha:
                # Choose kl2_min in kl2_min_list minimising the edit distance
                kl2_min = dist.minimise_levenshtein_distance(kl, kl2_min_list)
                # Add kl to the bag of kl2_min
                i = bagId(known_knowledges, kl2_min)
                known_knowledges[i].append(kl)
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
