#!/usr/bin/env python3

import diagnose as diag
import clustering as clust
import kltex as kl

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
    with open(notion_file) as nf:
        document, known_knowledges = kl.parse(nf)
        nf.close()
    undefined_knowledges = diag.parse(diagnose_file)
    with open(notion_file, "w") as nf: # otherwise, use sys.stdout as nf
        output = [[k] for k in undefined_knowledges]
        kl.writeDocument(nf, document, [], output)
        nf.close()

if __name__ == "__main__":
   main(sys.argv[1:])