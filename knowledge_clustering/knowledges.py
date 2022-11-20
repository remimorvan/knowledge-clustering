from __future__ import annotations

import toposort  # Topological sort pylint: disable=import-error
import knowledge_clustering.file_updater as fu

# import copy

_DISCARD_LINE = "%%%%% NEW KNOWLEDGES "


def flat(list_of_list):
    """Flattens a list of list into a single list."""
    return [x for y in list_of_list for x in y]


class Knowledges:
    def __init__(self, filename):
        """
        Reads a tex file from a file descriptor f.

        Args:
            filename: the name of a file containing knowledges.

        Computes:
            self.original_hash: the hash of the document ;
            self.document: a list of records, either of the form:
                {
                    "type"="tex",
                    "lines"= list of strings (the lines)
                }
                or {
                    "type"="knowledge",
                    "lines"= list of strings (the lines)
                    "command" = string representing the line introducing the knowledge,
                    "number" = the number of the knowledge
                }
            self.known_knowledges: a list of list of strings.
                Each list of strings contains strings corresponding to the same knowledge.
                The position in the string corresponds to the "number" field in the above
                document description.
        """
        self.bags = []  # Lists of lists, containing knowledges.
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
                return line == _DISCARD_LINE

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
            self.bags = knowledges
            self.nb_known_bags = len(self.bags)
            self.length_known_bags = [len(bag) for bag in self.bags]
            self.compute_dependency_graph()

    def get_all_bags(self):
        """Returns all bags that were not added since the last checkpoint, as a list of lists of strings."""
        return self.bags

    def get_new_bags(self):
        """Returns all bags that were not added since the last checkpoint, as a list of lists of strings."""
        return self.bags[self.nb_known_bags :]

    def get_all_knowledges(self):
        """Returns all knowledges, as a list of strings."""
        return flat(self.bags)

    def get_known_knowledges_in_bag(self, id):
        """Returns the list of knowledges contained in the `id`-th bag
        during the last checkpoint, as a list of strings."""
        if id < self.nb_known_bags:
            return self.bags[id][: self.length_known_bags[id]]
        else:
            return []

    def get_new_knowledges_in_bag(self, id):
        """Returns the list of knowledges contained in the `id`-th bag
        that were added since the last checkpoint, as a list of strings."""
        if id < self.nb_known_bags:
            return self.bags[id][self.length_known_bags[id] :]
        else:
            return self.bags[id]

    def add_new_bag(self, kl):
        """Adds a new bag that contains only the string `kl`."""
        self.bags.append([kl])

    def define_synonym_of(self, kl1, kl2):
        """
        Defines a new knowledge (string) `kl1` as a new synonym of the already
        existing knowledge (string) `kl2`.
        """
        for id, bag in enumerate(self.bags):
            if kl2 in bag:
                self.bags[id].append(kl1)
                return
        print(f"Error: {kl2} is not a knowledge.")

    def compute_dependency_graph(self):
        dependency = dict()
        dependency_reversed = dict()
        for s1 in self.get_all_knowledges():
            dependency[s1] = set(
                [s2 for s2 in self.get_all_knowledges() if s2 in s1 and s1 != s2]
            )
            dependency_reversed[s1] = set(
                [s2 for s2 in self.get_all_knowledges() if s1 in s2 and s1 != s2]
            )
        self.dependency = dependency
        self.all_knowledges_sorted = list(
            toposort.toposort_flatten(dependency_reversed)
        )

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
                    if b["number"] < self.nb_known_bags:
                        for kl in self.get_new_knowledges_in_bag(b["number"]):
                            file.write((f" | {kl}\n" if nocomment else f"%  | {kl}\n"))
            if len(self.get_new_bags()) > 0:
                file.write(_DISCARD_LINE + "\n")
                for bag in self.get_new_bags():
                    if len(bag) > 0:
                        file.write("%\n")
                        file.write("%\\knowledge{notion}\n")
                        for kl in bag:
                            file.write((f" | {kl}\n" if nocomment else f"%  | {kl}\n"))
