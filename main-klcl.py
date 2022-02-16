#!/usr/bin/env python3

import distance as dist
import diagnose as diag
import clustering as clust

import sys, getopt

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hn:d:",["notion=","diagnose"])
    except getopt.GetoptError:
        print("main-klcl.py -n <file_notion> -d <file_diagnose>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("main-klcl.py -n <file_notion> -d <file_diagnose>")
            sys.exit()
        elif opt in ("-n", "--notion"):
            notion_file = arg
        elif opt in ("-d", "--diagnose"):
            diagnose_file = arg
    dictNotion = diag.dictFromDiagnoseFile(diagnose_file)
    for scope in dictNotion:
        ag = clust.clusterNotions(dictNotion[scope])
        for l in ag:
            print("\knowledge{notion}")
            for no in l:
                scope_str = "" if scope == "" else "@"+scope
                print("\t| "+no+scope_str)
            print("")

if __name__ == "__main__":
   main(sys.argv[1:])