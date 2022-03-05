import distance as dist
import clingo

def escapeBackslash(str):
    return str.replace("\\", "\\\\")

def writeKnownKnowledges(f, known_knowledges):
    # Takes a list of lists of known_knowledges, and
    # defines each knowledge kl as a known knowledge by declaring the predicate known(kl)).
    # Moreover, defines every bag of knownledges by writing a predicate bag(i) for every
    # integer indexing a bag, and by writing a predicate belongsTo(kl, i) when the knowledge
    # i belongs to the bag i.
    for bag_id, bag in enumerate(known_knowledges):
        f.write("bag(%i).\n" % bag_id)
        for kl in bag:
            f.write("known(\"%s\").\n" % escapeBackslash(kl))
            f.write("belongsTo(\"%s\", %i).\n" % (escapeBackslash(kl), bag_id))
        f.write("\n")

def writeUnknownKnowledges(f, unknown_knowledges):
    # Takes a list unknown_knowledges, and
    # defines each knowledge kl as an unknown knowledge by declaring the predicate unknown(kl)).
    for kl in unknown_knowledges:
        f.write("unknown(\"%s\").\n" % escapeBackslash(kl))
    f.write("\n")

def writeProximityPredicatesForDistance(f, kl1, kl2, alpha, beta):
    # if kl1 and kl2 are distinct knowledges:
    # - if they are at distance at most alpha, declare that they are near ;
    # - if they are at distance at least beta, declare that they are near.
    if kl1 != kl2:
        if dist.distance(kl1, kl2) <= alpha:
            f.write("near(\"%s\", \"%s\").\n" % (escapeBackslash(kl1), escapeBackslash(kl2)))
        elif dist.distance(kl1, kl2) >= beta:
            f.write("far(\"%s\", \"%s\").\n" % (escapeBackslash(kl1), escapeBackslash(kl2)))

def writeProximityPredicates(f, known_knowledges, unknown_knowledges, alpha, beta):
    # Takes a file f, known_knowledges and unknown_knowledges 
    # For every pair of distinct knowledges (kl1, kl2), writes either a predicate near(kl1, kl2),
    # or far(kl1, kl2), or nothing, according to the following rules:
    # - if kl1 and kl2 are known knowledges:
    # -- (a) if they belong to the same bag, they are near ;
    # -- (b) if they do not belong to the same bag, they are far ;
    # - if kl1 and kl2 are knowledges, at least one of which is unknown:
    # -- (c) if they are at distance at most alpha, they are near ;
    # -- (d) if they are at distance at least beta, they are far.
    for bag in known_knowledges: # Condition a
        for kl1 in bag:
            for kl2 in bag:
                if kl1 != kl2:
                    f.write("near(\"%s\", \"%s\").\n" % (escapeBackslash(kl1), escapeBackslash(kl2)))
    f.write("\n")
    for bag1_id, bag1 in enumerate(known_knowledges): # Condition b
        for bag2_id, bag2 in enumerate(known_knowledges):
            if bag1_id != bag2_id:
                for kl1 in bag1:
                    for kl2 in bag2:
                        f.write("far(\"%s\", \"%s\").\n" % (escapeBackslash(kl1), escapeBackslash(kl2)))
    f.write("\n")
    # Condition c and d
    for kl1 in unknown_knowledges:
        for kl2 in unknown_knowledges:
            writeProximityPredicatesForDistance(f, kl1, kl2, alpha, beta)
    for kl1 in unknown_knowledges:
        for bag in known_knowledges:
            for kl2 in bag:
                writeProximityPredicatesForDistance(f, kl1, kl2, alpha, beta)
                writeProximityPredicatesForDistance(f, kl2, kl1, alpha, beta)
    f.write("\n")

def writeAddEmptyBags(f, k, n):
    # Add n (empty) bags that are numbered k, ..., k+n-1
    if n > 0:
        f.write("bag(%i..%i).\n\n" % (k, k+n-1))

def writeProblem(f, known_knowledges, unknown_knowledges, alpha, beta):
    # Encodes the knowledges (known and unknown) and their proximity as contraints in ASP
    writeKnownKnowledges(f, known_knowledges)
    writeUnknownKnowledges(f, unknown_knowledges)
    writeAddEmptyBags(f, len(known_knowledges), len(unknown_knowledges))
    writeProximityPredicates(f, known_knowledges, unknown_knowledges, alpha, beta)

def solveProblem(kl_encoding, constraints_encoding, time_limit, nb_bags_defined):
    # Takes two file descriptors encoding the ASP problem and returns clingo's solution as a string
    # computing in time at most time_limit (in seconds).
    ctl = clingo.Control()
    ctl.add("kl", [], kl_encoding)
    ctl.add("constraints", [], constraints_encoding)
    ctl.ground([("kl", []), ("constraints", [])])
    # Solve the problem
    def on_model(x):
        global solution
        global nb_bags
        solution = ("%s" % x)
        nb_bags = x.cost[0]
    # Tries to find the optimal solution in time ≤ time_limit
    ctl.configuration.solve.opt_mode = 'opt'
    ctl.configuration.solve.models = 0
    with ctl.solve(on_model=on_model, async_=True) as handle:
        handle.wait(time_limit)
        handle.cancel()
    printMessageSolutionFound(nb_bags-nb_bags_defined)
    return solution

def printMessageSolutionFound(nb_new_bags):
    message = "Found a solution requiring to add "
    if nb_new_bags == 0:
        message = message + "no new notion."
    elif nb_new_bags == 1:
        message = message + "1 new notion."
    else:
        message = message + ("%i new notions." % nb_new_bags)
    print(message)