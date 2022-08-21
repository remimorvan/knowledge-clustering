from multiprocessing.sharedctypes import Value
import toposort  # Topological sort
import knowledge_clustering.file_updater as fu

# import copy

DISCARD_LINE = "%%%%% NEW KNOWLEDGES "


def flat(list_of_list):
    return [x for y in list_of_list for x in y]


class Knowledges:
    def __init__(self, filename):
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
            self.bags = knowledges
            self.nb_known_bags = len(self.bags)
            self.length_known_bags = [len(bag) for bag in self.bags]
            self.compute_dependency_graph()

    def get_all_bags(self):
        """Returns all bags that were not added since the last checkpoint."""
        return self.bags

    def get_new_bags(self):
        """Returns all bags that were not added since the last checkpoint."""
        return self.bags[self.nb_known_bags :]

    def get_all_knowledges(self):
        return flat(self.bags)

    def get_known_knowledges_in_bag(self, id):
        """Returns the list of knowledges contained in the `id`-th bag
        during the last checkpoint."""
        if id < self.nb_known_bags:
            return self.bags[id][: self.length_known_bags[id]]
        else:
            return []

    def get_new_knowledges_in_bag(self, id):
        """Returns the list of knowledges contained in the `id`-th bag
        that were added since the last checkpoint."""
        if id < self.nb_known_bags:
            return self.bags[id][self.length_known_bags[id] :]
        else:
            return self.bags[id]

    def add_new_bag(self, kl):
        """Add a new bag that contains only `kl`."""
        self.bags.append([kl])

    def define_synonym_of(self, kl1, kl2):
        """Defines `kl1` as a new synonym of `kl2`."""
        for id, bag in enumerate(self.bags):
            if kl2 in bag:
                self.bags[id].append(kl1)
                return
        print(f"Error: {kl2} is not a knowledge.")

    # def __get_id(self, lst, kl):
    #     """Given a list of lists of strings `lst` and a string `kl`, returns
    #     a pair (boolean, natural number), describing if `kl` belongs to `lst`,
    #     and if so, the id of the list containg `kl`."""
    #     for i in range(len(lst)):
    #         if kl in lst[i]:
    #             return (True, i)
    #     return (False, -1)

    # def __fst_elements(self, lst):
    #     return list(map(lambda x: x[0], lst))

    # def is_known(self, kl):
    #     """Finds if a string `kl` is a known knowledge. Returns a pair consisting of a boolean
    #     and, if the knowledge was found, the id of the bag containing it."""
    #     return self.__get_id(self.known_knowledges, kl)

    # def is_new_knowledge(self, kl):
    #     """Finds if a string `kl` is a new knowledge. Returns a pair consisting of a boolean
    #     and, if the knowledge was found, the id of the bag containing it."""
    #     return self.__get_id(self.new_knowledges, kl)

    # def is_new_synonym(self, kl):
    #     """Finds if a string `kl` is a new synonym. Returns a pair consisting of a boolean
    #     and, if the knowledge was found, the id of the bag containing it."""
    #     return self.__get_id(self.new_synonyms, kl)

    # def is_knowledge(self, kl):
    #     """Boolean describing whether the string `k` is a known knowledge, a new knowledge or
    #     a new synonym."""
    #     return (
    #         True in self.__fst_elements(self.is_known(kl))
    #         or True in self.__fst_elements(self.is_new_knowledge(kl))
    #         or True in self.__fst_elements(self.is_new_synonym(kl))
    #     )

    # def add_new_knowledge(self, kl_list):
    #     """Define the list of strings kl_list as a new knowledge bag."""
    #     kl_list_copy = copy.copy(kl_list)
    #     self.new_knowledges.append(kl_list_copy)
    #     self.all_new_knowledges.append(kl_list_copy)

    # def define_synonym(self, kl1, kl2):
    #     (bl, id) = self.is_known(self, )

    # def update_flatten(self):
    #     flat = lambda l: [y for x in l for y in x]
    #     self.all_known_knowledges = flat(self.known_knowledges)
    #     self.all_new_knowledges = flat(self.new_knowledges)
    #     self.all_new_synonyms = flat(self.new_synonyms)
    #     self.all_knowledges = (
    #         self.all_known_knowledges + self.all_new_knowledges + self.all_new_synonyms
    #     )

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

    # def add_new_synonyms(self, new_synonyms):
    #     """Adds new synonyms."""
    #     n = len(self.new_synonyms)
    #     self.new_synonyms = [self.new_synonyms[i] + new_synonyms[i] for i in range(n)]
    #     self.update_flatten()
    #     self.compute_dependency_graph()

    # def add_new_knowledges(self, new_knowledges):
    #     """Adds new knowledges."""
    #     self.new_knowledges = self.new_knowledges + new_knowledges
    #     self.update_flatten()
    #     self.compute_dependency_graph()

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
                file.write(DISCARD_LINE + "\n")
                for bag in self.get_new_bags():
                    if len(bag) > 0:
                        file.write("%\n")
                        file.write("%\\knowledge{notion}\n")
                        for kl in bag:
                            file.write((f" | {kl}\n" if nocomment else f"%  | {kl}\n"))
