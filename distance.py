

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
    # Returns the substring of a notion that should be considered when computing the distance between two notions
    # Obtained by removing math, commands, spaces, dashes, and by writing the notion in lowercase.
    notion_norm = notion
    while '$' in notion_norm:
        sp = notion_norm.split("$",2)
        if len(sp) <= 1:
            break
        notion_norm = sp[0] + sp[2]
    while '\\' in notion_norm and ' ' in notion_norm:
        sp = notion_norm.split("\\", 1)
        sp2 = (sp[1]).split(" ", 1)
        if len(sp2) == 0:
            break
        notion_norm = sp[0] + sp2[1]
    while notion_norm[0] in [' ', '-']:
        notion_norm = notion_norm[1:]
    while notion_norm[-1] in [' ', '-']:
        notion_norm = notion_norm[:-1]
    notion_norm = notion_norm.replace(" ", "")
    notion_norm = notion_norm.replace("-", "")
    return notion_norm.lower()

def extractScope(notion):
    # Given a notion of the form "knowledge@scope" or "knowledge",
    # returns a pair consisting of the knowledge and the (possibly empty) scope.
    if '@' in notion:
        s = notion.split('@',1)
        return s[0], s[1]
    else:
        return notion, ""


def distance(notion1, notion2):
    # measures the distance between two strings
    notion_norm1 = normaliseNotion(notion1)
    knowledge1, scope1 = extractScope(notion_norm1)
    notion_norm2 = normaliseNotion(notion2)
    knowledge2, scope2 = extractScope(notion_norm2)
    if scope1 == scope2:
        n = (len(knowledge1)+len(knowledge2))/2
        return 1 - commonFactor(knowledge1, knowledge2)/n
    if scope1 != "" and scope2 != "" and scope1 != scope2:
        return 1
    else: 
        if scope2 != "":
            knowledge1, scope1, knowledge2, scope2 = knowledge2, scope2, knowledge1, scope1
        # Now scope2 is empty
        n = (len(knowledge1+scope1)+len(knowledge2))/2
        cf1 = commonFactor(scope1+knowledge1, knowledge2)
        cf2 = commonFactor(knowledge1+scope1, knowledge2)
        return 1 - max(cf1, cf2)/n