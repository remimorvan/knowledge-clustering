# functions for parsing and writing the tex file.



def parse(filename):
    # reads a tex file. Identifies the knowledge commands.
    with open(filenme) as f:
        context = []
        lines = f.readlines()
        knowledges = []
        currentBlock = []
        readingMode = 0
        for line in lines:
            if readingMode == 0:
                if lineIfKnowledge(line):
                    content.append(currentBlock)
                    currentBlock = []
                else:

            elif readingMode ==1:

            else

            context.append(line)
        return context

def lineIsKnowledge(line):
    return line.startswith("\\knowledge{");

def barKnowledgeFromLine(line):
    line = line.strip()
    if line.startswith("|"):
        return line[1:].strip()
    else
        return

def lineIsCommentBarKnowledgeFromLine(line):
    line = line.strip()
    if line.startswith("%"):
        return (line[1:].strip()).startwith("|")
    else
        return false
