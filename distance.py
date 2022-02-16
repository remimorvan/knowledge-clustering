

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

def normaliseNotion(notion):
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

def distance(notion1, notion2):
    # measures the distance between two strings
    notionMod1 = normaliseNotion(notion1)
    notionMod2 = normaliseNotion(notion2)
    n = (len(notionMod1)+len(notionMod2))/2
    return commonFactor(notionMod1, notionMod2)/n
