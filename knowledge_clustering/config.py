"""Parse a configuration file."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9
from pathlib import Path

import configparser


class ListConfigParser(configparser.ConfigParser):
    """Extended Config Parser to handle lists."""

    def getlist(self, section, option):
        """Return list in some config file."""
        value = self.get(section, option)
        return list(x.split("#")[0].strip() for x in value.splitlines())

    # def getlistint(self, section, option):
    #     return [int(x) for x in self.getlist(section, option)]


def parse(filename: Path) -> list[str]:
    """
    Reads a config file and returns the list of words occuring
    under the keyphrase `[DEFAULT] PREFIXES_SIMILAR=`.

    Args:
        filename: the name of a config file.

    Returns:
        a list of prefixes that should be ignored by the clustering algorithm.
    """
    p = ListConfigParser()
    p.read(filename)
    return p.getlist("DEFAULT", "PREFIXES_SIMILAR")
