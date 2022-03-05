#!/usr/bin/env python3

import diagnose as diag
import kltex
import call_asp
import parse_asp

import sys, getopt

FILE_ASP_CONSTRAINT = "constraints.lp"
ALPHA = 0.2
BETA = 0.55

def main(argv):
    compute_optimal = False
    try:
        opts, args = getopt.getopt(argv,"h:n:d:o:",["help", "notion", "diagnose","optimal"])
        opts_name = [a for (a, b) in opts]
        if "-n" not in opts_name and "--notion" not in opts_name and "-h" not in opts_name and "--help" not in opts_name:
            raise getopt.GetoptError("")
        if "-d" not in opts_name and "--diagnose" not in opts_name and "-h" not in opts_name and "--help" not in opts_name:
            raise getopt.GetoptError("")
    except getopt.GetoptError:
        print("Invalid syntax:\nDisplay help using 'anakin.py --help'.")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print("Syntax: 'anakin.py [mandatory arguments] [options]' where the mandatory arguments are\n * '-n <file_notion>' or '--notion <file_notion>\n * '-d <file_diagnose>' or '--diagnose <file_diagnose>'\nand the options are\n * '-o' or '--optimal': asks for the optimal solution.")
            sys.exit()
        elif opt in ("-n", "--notion"):
            notion_file = arg
        elif opt in ("-d", "--diagnose"):
            diagnose_file = arg
        elif opt in ("-o", "--optimal"):
            compute_optimal = True
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
        solution = call_asp.solveProblem(kl_encoding, constraints_encoding, compute_optimal)
        # Reopens the knowledge file and writes the new knowledges in it
        n = len(known_knowledges)
        with open(notion_file, "w") as f_kl:
            parse_asp.writeFromASPOutput(solution, f_kl, document, n)

if __name__ == "__main__":
   main(sys.argv[1:])