# functions for handling the diagnose file.
# - reading with "dictFromDiagnoseFile"


def dictFromDiagnoseFile(filename):
    # Returns the dictionnary of notions (indexed by scopes) from a filename
    dictNotion = dict()
    with open(filename) as f:
        lines = f.readlines()
        readingUndefinedKl = 0
        for l in lines:
            if readingUndefinedKl == 0 and "Undefined knowledges" in l:
                readingUndefinedKl = 1
            if readingUndefinedKl == 2 and "************************" in l:
                readingUndefinedKl = 0
            if readingUndefinedKl == 1 and "************************" in l:
                readingUndefinedKl = 2
            if readingUndefinedKl == 2 and "| " in l:
                str = (l.split("| ", 1)[1]).split("\n",1)[0]
                if "@" in str:
                    str_split = str.split("@")
                    notion, scope = str_split[0], str_split[1]
                else:
                    notion, scope = str, ""
                if scope in dictNotion:
                    dictNotion[scope].add(notion)
                else:
                    dictNotion[scope] = set()
                    dictNotion[scope].add(notion)
        f.close()
    return dictNotion
