# functions for handling the diagnose file.
# - reading with "parse"


def automata_line(state, line):
    """
    Automata parsing knowledges.
    0: waiting for knowledge block
    1: seen the heading of a knowledge block
    2: we are in a knowledge block
    """
    if state == 0 and "Undefined knowledges" in line:
        return 1, None
    elif state == 1 and "************************" in line:
        return 2, None
    elif (state == 2 or state == 0) and "************************" in line:
        return 0, None
    elif state == 2 and "| " in line:
        s = (line.split("| ", 1)[1]).split("\n", 1)[0]
        return 2, s
    else:
        return state, None


def unroll(automata, initial_state, generator):
    state = initial_state
    for y in generator:
        state, z = automata(state, y)
        yield z


def parse(filename):
    with open(filename) as f:
        list_notions = []
        for notion in unroll(automata_line, 0, f.readlines()):
            if notion is not None and notion not in list_notions:
                list_notions.append(notion)
    return list(list_notions)
