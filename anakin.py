#!/usr/bin/env python3

import diagnose as diag
import kltex
import call_asp
import parse_asp

import sys, getopt

FILE_ASP_CONSTRAINT = "constraints.lp"
ALPHA = 0.2
BETA = 0.6

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hn:d:",["notion=","diagnose"])
    except getopt.GetoptError:
        print("anakin.py -n <file_notion> -d <file_diagnose>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("anakin.py -n <file_notion> -d <file_diagnose>")
            sys.exit()
        elif opt in ("-n", "--notion"):
            notion_file = arg
        elif opt in ("-d", "--diagnose"):
            diagnose_file = arg
    # Get known and unknown knowledges from input files
    with open(notion_file, "r") as f_kl:
        document, known_knowledges = kltex.parse(f_kl)
        f_kl.close()
    unknown_knowledges = diag.parse(diagnose_file)
    if len(unknown_knowledges) > 0:
        # Writes the knowledges in ASP
        with open(".knowledges.lp", "w") as f_asp:
            call_asp.writeProblem(f_asp, known_knowledges, unknown_knowledges, ALPHA, BETA)
            f_asp.close()
        # Reads the two ASP files (knowledges and constraints)
        with open(".knowledges.lp", "r") as f_asp:
            kl_encoding = f_asp.read()
            f_asp.close()
        with open(FILE_ASP_CONSTRAINT, "r") as f_asp:
            constraints_encoding = f_asp.read()
            f_asp.close()
        # Solves the ASP optimisation problem
        solution = call_asp.solveProblem(kl_encoding, constraints_encoding)
        # Reopens the knowledge file and writes the new knowledges in it
        n = len(known_knowledges)
        with open(notion_file, "w") as f_kl:
            parse_asp.writeFromASPOutput(solution, f_kl, document, n)

if __name__ == "__main__":
   main(sys.argv[1:])