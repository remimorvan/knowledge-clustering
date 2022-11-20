from __future__ import annotations

import configparser


class ListConfigParser(configparser.ConfigParser):
    """Extended Config Parser to handle lists"""

    def getlist(self, section, option):
        value = self.get(section, option)
        return list(x.split("#")[0].strip() for x in value.splitlines())

    def getlistint(self, section, option):
        return [int(x) for x in self.getlist(section, option)]


def parse(filename):
    p = ListConfigParser()
    p.read(filename)
    return p.getlist("DEFAULT", "PREFIXES_SIMILAR")
