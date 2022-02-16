# functions for parsing and writing the tex file.



def parse(f):
    # reads a tex file. Identifies the knowledge commands.
    # outputs a pair (document,knowledges) of:
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
            if readingMode == "tex":
                document.append({"type":"tex","lines":currentBlock})
                currentBlock = []
            elif readingMode == "knowledge":
                document.append({"type":"knowledge","lines":currentBlock,"command": currentKnowledgeCommand,"number":len(knowledges)})
                currentBlock = []
                currentKnowledgeCommand = ""
                knowledges.append(currentKnowledgeStrings)
                currentKnowledgeStrings = []

        for line in lines:
            if line[-1]=="\n":
                line = line[:-1]
            if lineIsKnowledge(line):
                pushBlock()
                readingMode = "knowledge"
                currentKnowledgeCommand = line
                currentBlock = [line]
                currentKnowledgeStrings = []
            elif readingMode == "tex": #tex-mode
                currentBlock.append(line)
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
                    currentBlock=[line]

        if len(currentBlock)>0:
            pushBlock()
        return (document,knowledges)

def lineIsKnowledge(line):
    return line.startswith("\\knowledge{");

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
        print(k);

def printDocument(document):
    for b in document:
        for l in b["lines"]:
            print(l)

def writeDocument(f,document,updated_knowledges,new_knowledges):
    for b in document:
        if b["type"]=="tex":
            for l in b["lines"]:
                f.write(l+"\n")
        elif b["type"]=="knowledge":
            f.write(b["command"]+"\n")
            if b["number"]<len(updated_knowledges):
                for k in updated_knowledges[b["number"]]:
                    f.write("  | "+k+"\n")

with open("tmp.tex") as f:
    document,knowledges = parse(f)
    f.close()
    
with open("tmp.tex","w") as f:
    writeDocument(f,document,knowledges,[])
