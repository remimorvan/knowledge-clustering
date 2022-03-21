#!/usr/bin/env python3

import knowledge_clustering.diagnose as diag
import knowledge_clustering.kltex as kltex
import knowledge_clustering.clustering as clust
import knowledge_clustering.config as config
import knowledge_clustering.scope_meaning as sm
import argparse
import os
import nltk

ALPHA = 0
DIRNAME = os.path.dirname(__file__)
TEMP_FILE = os.path.join(DIRNAME, ".temp_knowledges.tex")
CONFIG_FILE = os.path.join(DIRNAME, "config/english.txt")

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--notion", help="File containing the knowledges/notions defined by the user.", type=str, dest="notion_file", required=True)
    parser.add_argument("-d", "--diagnose", help="File containing the diagnose file produced by TeX.", type=str, dest="diagnose_file", required=True)
    parser.add_argument("-l", "--lang", help="Language of your TeX document.", type=str, choices={"en"}, default="en", dest="lang")
    parser.add_argument("-s", "--scope", help="Print the scopes defined in the notion file and print the possible meaning of those scope infered by Knowledge-Clustering.", action="store_true", dest="print_scope")
    return parser.parse_args()

def main():
    args = parseArguments()
    with open(args.notion_file, "r") as f:
        document, known_knowledges = kltex.parse(f)
        f.close()
        list_prefixes = config.parse(CONFIG_FILE)
        scopes_meaning = sm.inferAllScopes(known_knowledges)
        if args.print_scope:
            sm.printScopes(scopes_meaning, print_meaning=True)
        unknown_knowledges = diag.parse(args.diagnose_file)
        if len(unknown_knowledges) > 0:
            len_known_knowledges = len(known_knowledges)
            len_bags = [len(bag) for bag in known_knowledges]
            # Add every unknown knowledge to a (possibly new) bag in known_knowledges
            clust.clustering(known_knowledges, unknown_knowledges, ALPHA, list_prefixes, scopes_meaning)
            # Compute updated_knowledges and new_knowledges
            new_knowledges = known_knowledges[len_known_knowledges:]
            updated_knowledges = [known_knowledges[bag_id][len_bags[bag_id]:] for bag_id in range(len_known_knowledges)]
            print("Found a solution by adding %i new bag(s)." % len(new_knowledges))
            with open(TEMP_FILE, "w") as f:
                kltex.writeDocument(f, document, updated_knowledges, new_knowledges)
                f.close()
                os.replace(TEMP_FILE, args.notion_file)

def main_download_nltk_data():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')