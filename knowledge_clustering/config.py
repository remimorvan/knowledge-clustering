def parse(filename):
    # Parse the list of prefixes that do not change the meaning 
    list_prefixes = []
    readingMode = "discard"
    with open(filename, "r") as f:
        for line in f.readlines():
            if line.startswith(":PREFIXES_SIMILAR"):
                readingMode = "prefix"
            elif line.startswith(":"):
                readingMode = "discard"
            else:
                line = line.split("%", 1)[0] # Remove everything after a `percent` symbol (comments)
                if readingMode == "prefix":
                    p = line.replace("\t", "").replace("\n", "").replace(" ", "")
                list_prefixes.append(p)
        f.close()
    if "" not in list_prefixes:
        list_prefixes.append("")
    return list_prefixes