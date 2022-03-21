import copy
import nltk
import nltk.stem.snowball as nss
stemmer = nss.SnowballStemmer("english")

IMPORTANT_POS = ["CD", "JJ", "JJR", "JJS", "NN", "NNP", "NNS", "PDT", "RB", "RBR", "RBS", "VB",
    "VBD", "VBG", "VBN", "VBP", "VBZ"]
INFINITY = 1000

# ---
# Functions to extract content from strings
# ---

def extractScope(notion):
    # Given a notion of the form "knowledge@scope" or "knowledge",
    # returns a pair consisting of the knowledge and the (possibly empty) scope.
    if '@' in notion:
        s = notion.split('@',1)
        return s[0], s[1]
    else:
        return notion, ""

def normaliseNotion(notion):
    # Returns the substring of a notion obtained by removing math and commands.
    notion_norm = notion
    while '$' in notion_norm:
        sp = notion_norm.split("$",2)
        if len(sp) <= 1:
            break
        notion_norm = sp[0] + sp[2]
    while '\\' in notion_norm:
        # If the notion contains a backslash, remove every letter following the backslash
        # see https://tex.stackexchange.com/a/34381/206008 for naming conventions of TeX commands
        sp = notion_norm.split("\\", 1)
        pref, suff = sp[0], sp[1]
        i = 0
        while i < len(suff) and suff[i].isalpha():
            i += 1
        notion_norm = pref + suff[i:]
    return notion_norm

def breakupNotion(notion):
    # Given a notion, returns the list of important words in kl, and the (possibly empty scope).
    # Important words are obtained by only keeping cardinals, preposition or conjunction, subordinating,
    # adjectives, nouns, pre-determiners, adverbs, verbs
    kl, scope = extractScope(normaliseNotion(notion))
    words_with_POStag = nltk.pos_tag(nltk.word_tokenize(kl))
    important_words = set([w for (w, pos) in words_with_POStag if pos in IMPORTANT_POS])
    return (important_words, scope)


# ---
# Computing the distance between two notions
# ---

def similarWords(w1, w2, list_prefixes):
    # Checks if two words w1 and w2 are similar up to taking their stem (removing a suffix)
    # and removing a prefix in the list `list_prefixes`.
    if w1 == w2:
        return True
    else:
        s1 = stemmer.stem(w1)
        s2 = stemmer.stem(w2)
        for p in list_prefixes:
            if p + s1 == s2 or p + s2 == s1:
                return True
        return False

def distance_sets_of_words(set_words1, set_words2, list_prefixes):
    # Given two sets of words (considered up to permutation), computes the distance between them.
    for w1 in set_words1:
        similar_to_w1 = [w2 for w2 in set_words2 if similarWords(w1, w2, list_prefixes)]
        # If you find a pair of similar words, remove them.
        if len(similar_to_w1) > 0:
            w2 = similar_to_w1[0]
            set_words1.remove(w1)
            set_words2.remove(w2)
            return distance_sets_of_words(set_words1, set_words2, list_prefixes)
    return(len(set_words1) + len(set_words2))

def distance(notion1, notion2, list_prefixes, scopes_meaning):
    # Measures the distance between two notions, given a list of prefixes to ignore and
    # a list of possible meaning for each scope
    kl1_words, sc1 = breakupNotion(notion1)
    kl2_words, sc2 = breakupNotion(notion2)
    if sc1 != "" and sc2 != "" and sc1 != sc2:
        return INFINITY
    elif len(kl1_words) == 0 or len(kl2_words) == 0:
        # Can happen in the notion is a command
        return INFINITY
    elif sc1 == sc2:
        return distance_sets_of_words(kl1_words, kl2_words, list_prefixes)
    else: 
        if sc1 == "":
            kl1_words, sc1, kl2_words, sc2 = kl2_words, sc2, kl1_words, sc1
        # sc2 is empty and sc1 isn't
        # return the minimal distance obtained by replacing sc1 by one of its possible meanings 
        dist = INFINITY
        if sc1 in scopes_meaning:
            sc1_meaning = scopes_meaning[sc1]
        else:
            sc1_meaning = [[sc1]]
        for meaning in sc1_meaning:
            kl1_with_meaning = list(copy.copy(kl1_words))
            kl1_with_meaning = set(kl1_with_meaning + meaning)
            dist = min(dist, distance_sets_of_words(kl1_with_meaning, kl2_words, list_prefixes))
        return dist

# --- 
# Misc 
# ---

# def commonFactor(s1, s2):
#     # Computes the length of the biggest common factor to s1 and s2
#     m = len(s1)
#     n = len(s2)
#     if m > n:
#         m, n = n, m
#         s1, s2 = s2, s1
#     maxCommonFactor = 0
#     for i in range(m):
#         for j in range(i+1,m+1):
#             if j-i > maxCommonFactor and s1[i:j] in s2:
#                 maxCommonFactor = j-i
#     return maxCommonFactor