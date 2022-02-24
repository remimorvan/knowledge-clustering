# functions for handling the diagnose file.
# - reading with "parse"


def parse(filename):
    # Returns the dictionnary of notions (indexed by scopes) from a filename
    listNotion = []
    with open(filename) as f:
        lines = f.readlines()
        reading_undefined_kl = 0
        for l in lines:
            if reading_undefined_kl == 0 and "Undefined knowledges" in l:
                reading_undefined_kl = 1
            if reading_undefined_kl == 2 and "************************" in l:
                reading_undefined_kl = 0
            if reading_undefined_kl == 1 and "************************" in l:
                reading_undefined_kl = 2
            if reading_undefined_kl == 2 and "| " in l:
                str = (l.split("| ", 1)[1]).split("\n",1)[0]
                listNotion.append(str)
        f.close()
    return list(set(listNotion))