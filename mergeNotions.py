#!/usr/local/bin/python3

def commonFactor(s1, s2):
    # Computes the length of the biggest common factor to s1 and s2
    m = len(s1)
    n = len(s2)
    if m > n:
        m, n = n, m
        s1, s2 = s2, s1
    maxCommonFactor = 0
    for i in range(m):
        for j in range(i+1,m+1):
            if j-i > maxCommonFactor and s1[i:j] in s2:
                maxCommonFactor = j-i
    return maxCommonFactor

def dictFromFile(filename):
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

def modifNotion(notion):
    # Returns the (substring) of a notion that should be considered when computing the distance between two notions
    # Obtained by removing any math and command
    notionSub = notion
    while '$' in notionSub:
        sp = notionSub.split("$",2)
        if len(sp) <= 1:
            break
        notionSub = sp[0] + sp[2]
    while '\\' in notionSub and ' ' in notionSub:
        sp = notionSub.split("\\", 1)
        sp2 = (sp[1]).split(" ", 1)
        if len(sp2) == 0:
            break
        notionSub = sp[0] + sp2[1]
    while notionSub[0] in [' ', '-']:
        notionSub = notionSub[1:]
    while notionSub[-1] in [' ', '-']:
        notionSub = notionSub[:-1]
    return notionSub

def score(notion1, notion2):
    notionMod1 = modifNotion(notion1)
    notionMod2 = modifNotion(notion2)
    n = (len(notionMod1)+len(notionMod2))/2
    return commonFactor(notionMod1, notionMod2)/n

def agregateNotion(setNotion, threshold=0.5):
    # Takes a set of notions and a threshold and returns a partition of
    # this set into lists of similar notions.
    # The greater the threshold, the finer the partition.
    processedNotions = dict() # assign to each notion an int-label such that
    # agreg[notion1] = agreg[notion2] iff notion1 and notion2 should be merged
    for notion in setNotion:
        similarNotions = [notion2 for notion2 in processedNotions if score(notion,notion2) >= threshold]
        if similarNotions != []:
            label = min([processedNotions[notion2] for notion2 in similarNotions])
            processedNotions[notion] = label
            for notion2 in similarNotions:
                processedNotions[notion2] = label
        else:
            i = 0
            while i in processedNotions.values():
                i += 1
            processedNotions[notion] = i
    # build a set of sets based on processedNotions
    agregatedNotions = []
    for i in set(processedNotions.values()):
        agregatedNotions.append([notion for notion in processedNotions if processedNotions[notion] == i])
    return agregatedNotions

dictNotion = dictFromFile("examples/ordinal-words.diagnose")
for scope in dictNotion:
    ag = agregateNotion(dictNotion[scope])
    for l in ag:
        print("\knowledge{notion}")
        for no in l:
            scope_str = "" if scope == "" else "@"+scope
            print("\t| "+no+scope_str)
        print("")
