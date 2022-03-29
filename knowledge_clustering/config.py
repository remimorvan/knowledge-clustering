import configparser

class ListConfigParser(configparser.ConfigParser):
    """Extended Config Parser to handle lists """
    def getlist(self,section,option):
        value = self.get(section,option)
        return list(filter(None, (x.strip() for x in value.splitlines())))

    def getlistint(self,section,option):
        return [int(x) for x in self.getlist(section,option)]

def parse(filename):
    p = ListConfigParser()
    p.read(filename)
    return p.getlist("DEFAULT", "PREFIXES_SIMILAR")

