import toposort  # Topological sort
import knowledge_clustering.file_updater as fu

DISCARD_LINE = "%%%%% NEW KNOWLEDGES "


class Knowledges:
    def __init__(self):
        # Lists of lists, containing knowledges.
        self.known_knowledges = []
        self.new_knowledges = []
        self.new_synonyms = []

    def is_known(self, k):
        """Finds if a string k is a known knowledges. Returns a pair consisting of a boolean
        and, if the knowledge was found, the id of the bag containing it."""
        for i in range(len(self.known_knowledges)):
            if k in self.known_knowledges[i]:
                return (True, i)
        return (False, -1)

    def update_flatten(self):
        flat = lambda l: [y for x in l for y in x]
        self.all_known_knowledges = flat(self.known_knowledges)
        self.all_new_knowledges = flat(self.new_knowledges)
        self.all_new_synonyms = flat(self.new_synonyms)
        self.all_knowledges = (
            self.all_known_knowledges + self.all_new_knowledges + self.all_new_synonyms
        )

    def read_knowledges_from_file(self, filename):
        """
        Reads a tex file from a file descriptor f.
        It identifies the knowledge commands and computes:
        - the hash of the document ;
        - document is a list of records, either of the form:
            {"type"="tex",
            "lines"= list of strings (the lines)}
        or {"type"="knowledge"
            "lines"= list of strings (the lines)
            "command" = string representing the line introducing the knowledge
            "number" = the number of the knowledge}
        - known_knowledges is a list of list of strings. Each list of strings contains strings corresponding to the same knowledge. The position in the string corresponds to the "number" field in the above document description.
        """
        self.filename = filename
        self.original_hash = fu.hash_file(filename)
        with open(filename) as file:
            lines = file.readlines()

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

            def lineIsDiscard(line):
                return line == DISCARD_LINE

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
            self.document = document
            self.known_knowledges = knowledges
            self.new_synonyms = [[] for _ in self.known_knowledges]
            self.update_flatten()
            self.compute_dependency_graph()

    def compute_dependency_graph(self):
        dependency = dict()
        dependency_reversed = dict()
        for s1 in self.all_knowledges:
            dependency[s1] = set(
                [s2 for s2 in self.all_knowledges if s2 in s1 and s1 != s2]
            )
            dependency_reversed[s1] = set(
                [s2 for s2 in self.all_knowledges if s1 in s2 and s1 != s2]
            )
        self.dependency = dependency
        self.all_knowledges_sorted = list(
            toposort.toposort_flatten(dependency_reversed)
        )

    def add_new_synonyms(self, new_synonyms):
        """Adds new synonyms."""
        n = len(self.new_synonyms)
        self.new_synonyms = [self.new_synonyms[i] + new_synonyms[i] for i in range(n)]
        self.update_flatten()
        self.compute_dependency_graph()

    def add_new_knowledges(self, new_knowledges):
        """Adds new knowledges."""
        self.new_knowledges = self.new_knowledges + new_knowledges
        self.update_flatten()
        self.compute_dependency_graph()

    def write_knowledges_in_file(self, nocomment=False):
        """
        Writes the new synonyms and new knowledges in the file containing the knowledges.
        """
        with fu.AtomicUpdate(self.filename, original_hash=self.original_hash) as file:
            for b in self.document:
                if b["type"] == "tex":
                    for l in b["lines"]:
                        file.write(l + "\n")
                elif b["type"] == "knowledge":
                    for l in b["lines"]:
                        file.write(l + "\n")
                    if b["number"] < len(self.new_synonyms):
                        for k in self.new_synonyms[b["number"]]:
                            file.write((f" | {k}\n" if nocomment else f"%  | {k}\n"))
            if len(self.new_knowledges) > 0:
                file.write(DISCARD_LINE + "\n")
                for k in self.new_knowledges:
                    if len(k) > 0:
                        file.write("%\n")
                        file.write("%\\knowledge{notion}\n")
                        for s in k:
                            file.write((f" | {s}\n" if nocomment else f"%  | {s}\n"))
