# functions for parsing and writing the tex file.


def parse(f):
    # reads a tex file from a file descriptor f.
    # It identifies the knowledge commands and outputs a pair (document,knowledges) consisting of:
    # - document is a list of records, either of the form:
    #      {"type"="tex",
    #       "lines"= list of strings (the lines)}
    #    or {"type"="knowledge"
    #       "lines"= list of strings (the lines)
    #       "command" = string representing the line introducing the knowledge
    #       "number" = the number of the knowledge}
    # - knowledges is a list of list of stringe. Each list of strings contains strings corresponding to the same knowledge. The position in the string corresponds to the "number" field in the above document description.
    lines = f.readlines()

    document = []
    knowledges = []

    readingMode = "tex"
    currentBlock = []
    currentKnowledgeCommand = ""
    currentKnowledgeStrings = []

    def pushBlock():
        nonlocal readingMode
        nonlocal document
        nonlocal currentBlock
        nonlocal currentKnowledgeCommand
        nonlocal currentKnowledgeStrings
        nonlocal knowledges
        nonlocal currentKnowledgeStrings
        if readingMode == "tex" and len(currentBlock) > 0:
            document.append({"type": "tex", "lines": currentBlock})
            currentBlock = []
        elif readingMode == "knowledge":
            document.append(
                {
                    "type": "knowledge",
                    "lines": currentBlock,
                    "command": currentKnowledgeCommand,
                    "number": len(knowledges),
                }
            )
            currentBlock = []
            currentKnowledgeCommand = ""
            knowledges.append(currentKnowledgeStrings)
            currentKnowledgeStrings = []

    for line in lines:
        if line[-1] == "\n":
            line = line[:-1]
        if readingMode == "discard" and not lineIsComment(line):
            readingMode = "tex"
        if lineIsDiscard(line):
            pushBlock()
            readingMode = "discard"
        elif lineIsKnowledge(line):
            pushBlock()
            readingMode = "knowledge"
            currentKnowledgeCommand = line
            currentBlock = [line]
            currentKnowledgeStrings = []
        elif readingMode == "knowledge":
            kl = barKnowledgeFromLine(line)
            if kl != None:
                currentBlock.append(line)
                currentKnowledgeStrings.append(kl)
            elif lineIsCommentBarKnowledgeFromLine(line):
                pass
            else:
                pushBlock()
                readingMode = "tex"
                currentBlock = [line]
        elif readingMode == "tex":
            currentBlock.append(line)
    pushBlock()
    return (document, knowledges)


discard_line = "%%%%% NEW KNOWLEDGES "


def lineIsDiscard(line):
    return line == discard_line


def lineIsComment(line):
    return line.startswith("%")


def lineIsKnowledge(line):
    return line.startswith("\\knowledge{")


def barKnowledgeFromLine(line):
    line = line.strip()
    if line.startswith("|"):
        return line[1:].strip()
    else:
        return


def lineIsCommentBarKnowledgeFromLine(line):
    line = line.strip()
    if line.startswith("%"):
        return (line[1:].strip()).startswith("|")
    else:
        return False


def printKnowledges(knowledges):
    for k in knowledges:
        print(k)


def printDocument(document):
    for b in document:
        for l in b["lines"]:
            print(l)


def writeDocument(f, document, updated_knowledges, new_knowledges):
    # Takes
    # - a file descriptor f
    # - a document as in "parse"
    # - updated_knowledges is a list of list of strings representinf knowledges.
    #     The effect is that list the string in item i get to be appended to the corresonding knowledge.
    # - a list of list of strings describing new knowledges to be suggested.
    # these will appended at the end of the document as comments ifmain
    # a block starting with discard_line and folowed by commented lines
    for b in document:
        if b["type"] == "tex":
            for l in b["lines"]:
                f.write(l + "\n")
        elif b["type"] == "knowledge":
            for l in b["lines"]:
                f.write(l + "\n")
            if b["number"] < len(updated_knowledges):
                for k in updated_knowledges[b["number"]]:
                    f.write("%  | " + k + "\n")
    if len(new_knowledges) > 0:
        f.write(discard_line + "\n")
        for k in new_knowledges:
            if len(k) > 0:
                f.write("%\n")
                f.write("%\\knowledge{notion}\n")
                for s in k:
                    f.write("%  | " + s + "\n")
