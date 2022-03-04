class UnknownPredicate(Exception):
    def __init__(self, name):
        self.name = name
        super().__init__("Predicate '%s' is unknown." % self.name)

def getFirstPredicate(solution):
    # Takes a solution (as a string containing predicates separated by spaces) and split it into
    # a single predicate and the rest of the solution
    n = len(solution)
    i = 0
    insideQuotationMarks = False # is character i between two quotation marks?
    while i < n:
        if solution[i] == '"':
            insideQuotationMarks = not insideQuotationMarks
        elif not insideQuotationMarks and solution[i] == ' ':
            return (solution[:i], solution[i+1:])
        i += 1
    return(solution, "")

def parsePredicate(str):
    # Takes a predicate as returned by clingo (e.g. 'belongsTo("word@ord",0)')
    # and returns the knowledge ("word@ord"), and the id of the bag it belongs to (here, it is 0).
    lst = str.split('(')
    predicate = str[0]
    if predicate == "belongsTo":
        lst = lst[1].split(')')
        lst = lst[0].split(',')
        return (lst[0], lst[1])

with open("solution.txt") as f:
    lines = f.read().splitlines()
    solution = lines[0]
    print(getAllPredicates(solution))
    raise UnknownPredicate("abc")