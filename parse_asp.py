import re
import kltex

class UnknownPredicate(Exception):
    def __init__(self, name):
        self.name = name
        super().__init__("Predicate '%s' is unknown." % self.name)

def getFirstPredicate(solution):
    # Takes a solution (as a string containing predicates separated by spaces) and split it into
    # a single predicate and the rest of the solution
    n = len(solution)
    i = 0
    inside_quotation_marks = False # is character i between two quotation marks?
    while i < n:
        if solution[i] == '"':
            inside_quotation_marks = not inside_quotation_marks
        elif not inside_quotation_marks and solution[i] == ' ':
            return (solution[:i], solution[i+1:])
        i += 1
    return(solution, "")

def parsePredicate(str):
    # Takes a predicate as returned by clingo (e.g. 'belongsToUnkown("word@ord",0)')
    # and returns the knowledge ("word@ord"), and the id of the bag it belongs to (here, it is 0).
    lst = str.split('(')
    predicate = lst[0]
    if predicate == "belongsToUnkown":
        lst = lst[1].split(')')
        lst = lst[0].split(',')
        return (lst[0], lst[1])
    else:
        raise UnknownPredicate(str[0])

def getParsedPredicates(f):
    lines = f.read().splitlines()
    solution = lines[0]
    parsed_predicates = []
    while solution != "":
        pred, solution = getFirstPredicate(solution)
        kl, bag_str = parsePredicate(pred)
        bag_id = int(bag_str)
        parsed_predicates.append(kl, bag_id)
    return parsed_predicates

def writeFromASPOutput(f_asp, f_kl, document, n):
    # Takes a file descriptor f_asp (answer of ASP solver), a file descriptor f_kl (of knowledges),
    # a document (parsed from f_kl), and the number n of bags that are already defined in said document.
    # Parse the new knowledges from f_asp and writes them in f.
    parsed_predicates = getParsedPredicates(f_asp)
    max_bag_id = max([bag_id for (_, bag_id) in parsed_predicates])
    updated_knowledges = [[] for i in range(n)]
    new_knowledges = [[] for i in range(max_bag_id-n+1)]
    for (kl, bag_id) in parsed_predicates:
        if bag_id < n:
            updated_knowledges[bag_id].append(kl)
        else:
            new_knowledges[bag_id - n].append(kl)
    while [] in new_knowledges:
        new_knowledges.remove([])
    kltex.writeDocument(f_kl, document, updated_knowledges, new_knowledges)

