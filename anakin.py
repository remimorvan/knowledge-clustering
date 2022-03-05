#!/usr/bin/env python3

import nbformat
import diagnose as diag
import kltex
import call_asp
import parse_asp

import sys, getopt

FILE_ASP_CONSTRAINT = "constraints.lp"
ALPHA = 0.25
BETA = 0.6

def main(argv):
    notion_file = ""
    diagnose_file = ""
    time_limit = 15
    try:
        opts, args = getopt.getopt(argv,"hn:d:t:",["help"])
    except getopt.GetoptError:
        print("Invalid syntax: display help using 'anakin.py --help'.")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print("Syntax: 'anakin.py [mandatory arguments] [options]' where the mandatory arguments are\n * '-n <file_notion>'\n * '-d <file_diagnose>' '\nand the options are\n * '-t': time limit, in seconds (default value is 15).")
            sys.exit()
        elif opt in ("-n"):
            notion_file = arg
        elif opt in ("-d"):
            diagnose_file = arg
        elif opt in ("-t"):
            time_limit = int(arg)
    if notion_file == "":
        print("Error: missing notion file.")
        sys.exit(2)
    if diagnose_file == "":
        print("Error: missing diagnose file.")
        sys.exit(2)
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
        nb_bags_defined = len(known_knowledges)
        solution = call_asp.solveProblem(kl_encoding, constraints_encoding, time_limit, nb_bags_defined)
        # Reopens the knowledge file and writes the new knowledges in it
        with open(notion_file, "w") as f_kl:
            parse_asp.writeFromASPOutput(solution, f_kl, document, nb_bags_defined)

if __name__ == "__main__":
   main(sys.argv[1:])