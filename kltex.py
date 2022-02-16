# functions for parsing and writing the tex file.



def parse(filename):
    # reads a tex file. Identifies the knowledge commands.
    with open(filename) as f:
        lines = f.readlines()
        f.close()

        document = []
        knowledgeList = []

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
            nonlocal knowledgeList
            nonlocal currentKnowledgeStrings
            if readingMode == "tex":
                document.append({"type":"tex","lines":currentBlock})
                currentBlock = []
            elif readingMode == "knowledge":
                document.append({"type":"knowledge","lines":currentBlock,"command": currentKnowledgeCommand,"number":len(knowledgeList)})
                currentBlock = []
                currentKnowledgeCommand = ""
                knowledgeList.append(currentKnowledgeStrings)
                currentKnowledgeStrings = []

        for line in lines:
            if readingMode == "tex": #tex-mode
                if lineIsKnowledge(line):
                    pushBlock()
                    readingMode = "knowledge"
                    currentKnowledgeCommand = line
                    currentBlock = [line]
                    currentKnowledgeStrings = []
                else:
                    currentBlock.append(line)
            elif readingMode == "knowledge":
                kl = barKnowledgeFromLine(line)
                if kl != None:
                    currentBlock.append(line)
                    currentKnowledgeStrings.append(kl)
                elif not lineIsCommentBarKnowledgeFromLine(line):
                    pushBlock()
                    readingMode = "tex"
                    currentBlock=[line]
        if len(currentBlock)>0:
            pushBlock()
        return document

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
        return (line[1:].strip()).startwith("|")
    else:
        return False


print(parse("tmp.tex"))
