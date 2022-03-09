#!/usr/bin/env python3

import nbformat
import diagnose as diag
import kltex
import clustering as clust
import sys, getopt
import os

ALPHA = 3
TEMP_FILE = ".temp_knowledges.tex"

def main(argv):
    notion_file = ""
    diagnose_file = ""
    time_limit = 15
    try:
        opts, args = getopt.getopt(argv,"hn:d:",["help"])
    except getopt.GetoptError:
        print("Invalid syntax: display help using 'anakin.py --help'.")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print("Syntax: 'anakin.py -n <file_notion> -d <file_diagnose>'.")
            sys.exit()
        elif opt in ("-n"):
            notion_file = arg
        elif opt in ("-d"):
            diagnose_file = arg
    if notion_file == "":
        print("Error: missing notion file.")
        sys.exit(2)
    if diagnose_file == "":
        print("Error: missing diagnose file.")
        sys.exit(2)
    # Get known and unknown knowledges from input files
    with open(notion_file, "r") as f:
        document, known_knowledges = kltex.parse(f)
        f.close()
        unknown_knowledges = diag.parse(diagnose_file)
        if len(unknown_knowledges) > 0:
            len_known_knowledges = len(known_knowledges)
            len_bags = [len(bag) for bag in known_knowledges]
            # Add every unknown knowledge to a (possibly new) bag in known_knowledges
            clust.clustering(known_knowledges, unknown_knowledges, ALPHA)
            # Compute updated_knowledges and new_knowledges
            new_knowledges = known_knowledges[len_known_knowledges:]
            updated_knowledges = [known_knowledges[bag_id][len_bags[bag_id]:] for bag_id in range(len_known_knowledges)]
            print("Found a solution by adding %i new bag(s)." % len(new_knowledges))
            with open(TEMP_FILE, "w") as f:
                kltex.writeDocument(f, document, updated_knowledges, new_knowledges)
                f.close()
                os.replace(TEMP_FILE, notion_file)
if __name__ == "__main__":
   main(sys.argv[1:])