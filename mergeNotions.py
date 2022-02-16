#!/usr/local/bin/python3

import distance as dist
import diagnose as diag
import clustering as clust


dictNotion = diag.dictFromDiagnoseFile("examples/ordinal-words.diagnose")

for scope in dictNotion:
    ag = clust.clusterNotions(dictNotion[scope])
    for l in ag:
        print("\knowledge{notion}")
        for no in l:
            scope_str = "" if scope == "" else "@"+scope
            print("\t| "+no+scope_str)
        print("")
