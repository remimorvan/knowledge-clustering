"""Manipulating known knowledges."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

from typing import NamedTuple
import toposort  # Topological sort pylint: disable=import-error

import knowledge_clustering.file_updater as fu
from knowledge_clustering import cst
from knowledge_clustering.misc import add_orange, add_bold


class DocInfoTex(NamedTuple):
    """Lines of a TeX document."""

    lines: list[str]


class DocInfoKnowledge(NamedTuple):
    """Lines of TeX document corresponding to the definition of a knowledge."""

    lines: list[str]
    command: str
    number: int


def flat(list_of_list):
    """Flattens a list of list into a single list."""
    return [x for y in list_of_list for x in y]


class Knowledges:
    def __init__(self, filename):
        """
        Reads a knowledge file from a file descriptor f.

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
        self.bags: list[list[str]] = []  # Lists of lists, containing knowledges.
        self.filename: str = filename
        self.original_hash = fu.hash_file(filename)
        with open(filename, encoding="utf-8") as file:
            lines: list[str] = file.readlines()

            document: list[DocInfoTex | DocInfoKnowledge] = []
            knowledges: list[list[str]] = []

            reading_mode: str = "tex"
            current_block: list[str] = []
            current_kl_cmd: str = ""
            current_kl_strs: list[str] = []

            def push_block():
                nonlocal reading_mode
                nonlocal document
                nonlocal current_block
                nonlocal current_kl_cmd
                nonlocal current_kl_strs
                nonlocal knowledges
                nonlocal current_kl_strs
                if reading_mode == "tex" and len(current_block) > 0:
                    document.append(DocInfoTex(lines=current_block))
                    current_block = []
                elif reading_mode == "knowledge":
                    document.append(
                        DocInfoKnowledge(
                            lines=current_block,
                            command=current_kl_cmd,
                            number=len(knowledges),
                        )
                    )
                    current_block = []
                    current_kl_cmd = ""
                    knowledges.append(current_kl_strs)
                    current_kl_strs = []

            def line_is_discard(line):
                return line == cst.DISCARD_LINE

            def line_is_comment(line):
                return line.startswith("%")

            def line_is_knowledge(line):
                return line.startswith("\\knowledge{")

            def bar_knowledge_from_line(line):
                line = line.strip()
                if line.startswith("|"):
                    return line[1:].strip()
                return None

            def line_is_comment_bar_knowledge_from_line(line):
                line = line.strip()
                if line.startswith("%"):
                    return (line[1:].strip()).startswith("|")
                return False

            for line in lines:
                if line[-1] == "\n":
                    line = line[:-1]
                if reading_mode == "discard" and not line_is_comment(line):
                    reading_mode = "tex"
                if line_is_discard(line):
                    push_block()
                    reading_mode = "discard"
                elif line_is_knowledge(line):
                    push_block()
                    reading_mode = "knowledge"
                    current_kl_cmd = line
                    current_block = [line]
                    current_kl_strs = []
                elif reading_mode == "knowledge":
                    kl = bar_knowledge_from_line(line)
                    if kl is not None:
                        current_block.append(line)
                        current_kl_strs.append(kl)
                    elif line_is_comment_bar_knowledge_from_line(line):
                        pass
                    else:
                        push_block()
                        reading_mode = "tex"
                        current_block = [line]
                elif reading_mode == "tex":
                    current_block.append(line)
            push_block()
            self.document = document
            self.bags = knowledges
            self.nb_known_bags: int = len(self.bags)
            self.length_known_bags: list[int] = [len(bag) for bag in self.bags]

    def get_all_bags(self) -> list[list[str]]:
        """Returns all bags as a list of lists of strings."""
        return self.bags

    def get_old_bags(self) -> list[list[str]]:
        """Returns all bags that were present at the last checkpoint,
        as a list of lists of strings."""
        return self.bags[: self.nb_known_bags]

    def get_new_bags(self) -> list[list[str]]:
        """Returns all bags that were not added since the last checkpoint,
        as a list of lists of strings."""
        return self.bags[self.nb_known_bags :]

    def get_all_knowledges(self) -> list[str]:
        """Returns all knowledges, as a list of strings."""
        return flat(self.bags)

    def get_known_knowledges_in_bag(self, b_id: int) -> list[str]:
        """Returns the list of knowledges contained in the `b_id`-th bag
        during the last checkpoint, as a list of strings."""
        if b_id < self.nb_known_bags:
            return self.bags[b_id][: self.length_known_bags[b_id]]
        return []

    def get_new_knowledges_in_bag(self, b_id: int) -> list[str]:
        """Returns the list of knowledges contained in the `id`-th bag
        that were added since the last checkpoint, as a list of strings."""
        if b_id < self.nb_known_bags:
            return self.bags[b_id][self.length_known_bags[b_id] :]
        return self.bags[b_id]

    def add_new_bag(self, kl: str) -> None:
        """Adds a new bag that contains only the string `kl`."""
        self.bags.append([kl])

    def define_synonym_of(self, kl1: str, kl2: str) -> None:
        """
        Defines a new knowledge (string) `kl1` as a new synonym of the already
        existing knowledge (string) `kl2`.
        """
        for b_id, bag in enumerate(self.bags):
            if kl2 in bag:
                self.bags[b_id].append(kl1)
                return
        print(f"Error: {kl2} is not a knowledge.")

    def was_changed(self) -> bool:
        """
        Returns whether kl has new bags or new synonyms.
        """
        if len(self.get_new_bags()) > 0:
            return True
        for b_id in range(len(self.get_old_bags())):
            if len(self.get_new_knowledges_in_bag(b_id)) > 0:
                return True
        return False

    def write_knowledges_in_file(self, nocomment: bool = False) -> None:
        """
        Writes the new synonyms and new knowledges in the file containing the knowledges.
        """
        with fu.AtomicUpdate(self.filename, original_hash=self.original_hash) as file:
            for b in self.document:
                if isinstance(b, DocInfoTex):
                    for l in b.lines:
                        file.write(l + "\n")
                elif isinstance(b, DocInfoKnowledge):
                    for l in b.lines:
                        file.write(l + "\n")
                    if b.number < self.nb_known_bags:
                        for kl in self.get_new_knowledges_in_bag(b.number):
                            file.write((f" | {kl}\n" if nocomment else f"%  | {kl}\n"))
            if len(self.get_new_bags()) > 0:
                file.write(cst.DISCARD_LINE + "\n")
                for bag in self.get_new_bags():
                    if len(bag) > 0:
                        file.write("%\n")
                        file.write("%\\knowledge{notion}\n")
                        for kl in bag:
                            file.write((f" | {kl}\n" if nocomment else f"%  | {kl}\n"))


class KnowledgesList:
    def __init__(self, kls_list: list[str]):
        """
        Reads a list of knowledge files.

        Args:
            kls_list: the list of filenames containing knowledges.
        """
        self.nb_file: int = len(kls_list)
        self.kls_list: list[Knowledges] = [
            Knowledges(filename) for filename in kls_list
        ]
        self.compute_dependency_graph()

    def get_all_kls_struct(self) -> list[Knowledges]:
        """Returns the list of all knowledge structures"""
        return self.kls_list

    def default_kls(self) -> Knowledges:
        """Returns the default kls."""
        return self.kls_list[self.nb_file - 1]

    def get_all_bags(self) -> list[list[str]]:
        """Returns all bags as a list of lists of strings."""
        return flat([kls.get_all_bags() for kls in self.kls_list])

    def get_all_knowledges(self) -> list[str]:
        """Returns all knowledges, as a list of strings."""
        return flat([kls.get_all_knowledges() for kls in self.kls_list])

    def get_sorted_knowledges(self) -> list[str]:
        """Returns all knowledges, sorted by topological sort."""
        return self.all_knowledges_sorted

    def add_new_bag(self, kl: str) -> None:
        """Adds a new bag that contains only the string `kl`."""
        self.default_kls().add_new_bag(kl)

    def define_synonym_of(self, kl1: str, kl2: str) -> None:
        """
        Defines a new knowledge (string) `kl1` as a new synonym of the already
        existing knowledge (string) `kl2`.
        """
        for kls in self.kls_list:
            for b_id, bag in enumerate(kls.bags):
                if kl2 in bag:
                    kls.bags[b_id].append(kl1)
                    return
        print(f"Error: {kl2} is not a knowledge.")

    def write_knowledges_in_file(self, nocomment: bool = False) -> None:
        """
        Writes the new synonyms and new knowledges in the file containing the knowledges.
        """
        for kls in self.kls_list:
            kls.write_knowledges_in_file(nocomment)

    def get_new_bags(self) -> list[list[str]]:
        """Returns all bags that were not added since the last checkpoint,
        as a list of lists of strings."""
        return self.default_kls().get_new_bags()

    def compute_dependency_graph(self) -> None:
        """
        Computes the dependency graph of all knowledges, for the substring relation.
        Then, sort all knowledges using topological sorting.
        Result are stored in self.dependency and self.all_knowledges_sorted.
        """
        dependency: dict[str, set[str]] = {}
        dependency_reversed: dict[str, set[str]] = {}
        for s1 in self.get_all_knowledges():
            dependency[s1] = {
                s2 for s2 in self.get_all_knowledges() if s2 in s1 and s1 != s2
            }
            dependency_reversed[s1] = {
                s2 for s2 in self.get_all_knowledges() if s1 in s2 and s1 != s2
            }
        self.dependency: dict[str, set[str]] = dependency
        self.all_knowledges_sorted: list[str] = list(
            toposort.toposort_flatten(dependency_reversed)
        )


def remove_redundant_files(list_filenames: list[str]) -> list[str]:
    """
    Given a list of filenames, return the same list without duplicates, and output a warning
    if there is such a duplicate.
    """
    output: list[str] = []
    for fn in list_filenames:
        if fn in output:
            print(
                add_bold(add_orange("[Warning]"))
                + f" same knowledge file given twice ({fn}), second occurrence is ignored."
            )
        else:
            output.append(fn)
    return output
