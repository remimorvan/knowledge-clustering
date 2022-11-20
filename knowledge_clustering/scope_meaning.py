# ---
# Infer the scope from known knowledges
# ---

from __future__ import annotations

import knowledge_clustering.distance as dist
import copy


def union_list_of_lists(l1, l2):
    # Returns the union (without repetition) of two lists of lists
    s = copy.copy(l1)
    for sublist in l2:
        if sublist not in s:
            s.append(sublist)
    return s


def inferScope(list_kl, scope, lang):
    # Takes a list of knowledges that all belong to the same knowledge and a scope.
    # If the list contains a knowledge with this scope, we try to infer the meaning of the scope
    # by looking at similar knowledges.
    # Returns a list of strings.
    # Running the algorithm on ["word@some-scope", "countable ordinal word", "ordinal word", "scattered language"]
    # for the scope `some-scope` will return the list [["countable", "ordinal"], ["ordinal"]].
    result = []
    list_kl_broke = [dist.breakupNotion(kl, lang) for kl in list_kl]
    for (kl1_words, sc1) in list_kl_broke:
        if sc1 == scope:
            for (kl2_words, sc2) in list_kl_broke:
                if sc2 == "" and all([w in kl2_words for w in kl1_words]):
                    # If every word of kl1 appears in kl2 and kl2 has an empty scope,
                    # return the words in kl2 not appearing in kl1
                    result.append([w for w in kl2_words if w not in kl1_words])
    return result


def inferAllScopes(known_knowledges, lang):
    list_scopes = set(
        [sc for bag in known_knowledges for (_, sc) in map(dist.extractScope, bag)]
    )
    if "" in list_scopes:
        list_scopes.remove("")
    scopes_meaning = {sc: [] for sc in list_scopes}
    for scope in list_scopes:
        for bag in known_knowledges:
            scopes_meaning[scope] = union_list_of_lists(
                scopes_meaning[scope], inferScope(bag, scope, lang)
            )
        if [scope] not in scopes_meaning[scope]:
            scopes_meaning[scope].append([scope])
    return scopes_meaning


def printScopes(scopes_meaning, print_meaning=False):
    print("Defined scopes:")
    if not print_meaning:
        print("\t", list(scopes_meaning.keys()))
    else:
        for sc in scopes_meaning:
            print("\t@%s" % sc, ":", scopes_meaning[sc])
