"""Compute the distance between two knowledges."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

import copy
import nltk  # type: ignore
import nltk.stem.snowball as nss  # type: ignore
from unidecode import unidecode

from knowledge_clustering import cst


# ---
# Edit distance
# ---


def levenshtein_distance(s: str, t: str) -> int:
    """
    Computes the Levenshtein (insertions, deletions or substitutions are allowed)
    edit distance between two strings.
    """
    # Implementation of the Wagner–Fischer algorithm
    # https://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm
    m, n = len(s), len(t)
    dist = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
    for i in range(1, m + 1):
        dist[i][0] = i
    for j in range(1, n + 1):
        dist[0][j] = j
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            substitution_cost = 0 if s[i - 1] == t[j - 1] else 1
            dist[i][j] = min(
                dist[i - 1][j] + 1,
                dist[i][j - 1] + 1,
                dist[i - 1][j - 1] + substitution_cost,
            )
    return dist[m][n]


def minimise_levenshtein_distance(s: str, t_list: list[str]) -> str:
    """
    Given a string s, and a non-empty list of strings, returns an element of t_list
    minimising the edit distance with s.
    """
    t_min = t_list[0]
    dist_min = levenshtein_distance(s, t_min)
    for t in t_list[1:]:
        dist = levenshtein_distance(s, t)
        if dist < dist_min:
            t_min = t
            dist_min = dist
    return t_min


# ---
# Functions to extract content from strings
# ---


def extract_scope(notion: str) -> tuple[str, str]:
    """
    Given a notion of the form "knowledge@scope" or "knowledge",
    returns a pair consisting of the knowledge and the (possibly empty) scope.
    """
    if "@" in notion:
        s = notion.split("@", 1)
        return s[0], s[1]
    return notion, ""


def normalise_notion(notion: str) -> str:
    """
    Returns the substring of a notion obtained by removing math, commands, accents
    and non-brekable spaces.
    """
    notion_norm = notion
    while "$" in notion_norm:
        sp = notion_norm.split("$", 2)
        if len(sp) <= 1:
            break
        notion_norm = sp[0] + sp[2]
    for remove_char in cst.IGNORE_CHAR_BACKSLASH:
        while remove_char in notion_norm:
            # If the notion contains remove_char, remove it.
            sp = notion_norm.split(remove_char, 1)
            notion_norm = sp[0] + sp[1]
    while "\\" in notion_norm:
        # If the notion contains a backslash, remove every letter following the backslash
        # see https://tex.stackexchange.com/a/34381/206008 for naming conventions of TeX commands
        sp = notion_norm.split("\\", 1)
        pref, suff = sp[0], sp[1]
        i = 0
        while i < len(suff) and suff[i].isalpha():
            i += 1
        notion_norm = pref + suff[i:]
    for remove_char in cst.IGNORE_CHAR_NO_BACKSLASH:
        while remove_char in notion_norm:
            # If the notion contains remove_char, remove it.
            sp = notion_norm.split(remove_char, 1)
            notion_norm = sp[0] + sp[1]
    for space_char in cst.SPACE_CHAR:
        while space_char in notion_norm:
            # If the notion contains remove_char, replace it with a space.
            sp = notion_norm.split(space_char, 1)
            notion_norm = sp[0] + " " + sp[1]
    return unidecode(notion_norm)  # Ascii-fy (in particular, remove accents) the result


def breakup_notion(notion: str, lang: str) -> tuple[list[str], str]:
    """
    Takes a notion, and a language, and returns
    a set of words contained in the notion.

    If the language is `english`, remove unimportant words.
    Important words are: cardinals, preposition or conjunction, subordinating,
    adjectives, nouns, pre-determiners, adverbs, verbs (list defined in cst.IMPORTANT_POS).

    """
    kl, scope = extract_scope(normalise_notion(notion))
    if lang == "english":
        words_with_POStag = nltk.pos_tag(  # pylint: disable=invalid-name
            nltk.word_tokenize(kl, language="english")
        )
        important_words = {
            w for (w, pos) in words_with_POStag if pos in cst.IMPORTANT_POS
        }
        return (list(important_words), scope)
    return (list(set(nltk.word_tokenize(kl, language=lang))), scope)


# ---
# Computing the distance between two notions
# ---


def similar_words(w1: str, w2: str, list_prefixes: list[str], stemmer) -> bool:
    """
    Checks if two words w1 and w2 are similar up to taking their stem (removing a suffix)
    and removing a prefix in the list `list_prefixes`.
    """
    if w1 == w2:
        return True
    for s1 in [w1, stemmer.stem(w1)]:
        for s2 in [w2, stemmer.stem(w2)]:
            for p in list_prefixes:
                for s in cst.IGNORE_SUFFIXES:
                    if p + s1 + s == s2 or s1 == p + s2 + s:
                        return True
    return False


def __semi_distance_sets_of_words(
    set_words1: list[str], set_words2: list[str], list_prefixes: list[str], stemmer
) -> tuple[int, int]:
    """
    Given two sets of words (considered up to permutation), computes the
    numbers of words of w1 that aren't close to a word of w2 and reciprocally.
    """
    for w1 in set_words1:
        similar_to_w1 = [
            w2 for w2 in set_words2 if similar_words(w1, w2, list_prefixes, stemmer)
        ]
        # If you find a pair of similar words, remove them.
        if len(similar_to_w1) > 0:
            w2 = similar_to_w1[0]
            set_words1.remove(w1)
            set_words2.remove(w2)
            return __semi_distance_sets_of_words(
                set_words1, set_words2, list_prefixes, stemmer
            )
    return (len(set_words1), len(set_words2))


def inclusion_sets_of_words(
    set_words1: list[str], set_words2: list[str], list_prefixes: list[str], stemmer
) -> bool:
    """
    Given two sets of words (considered up to permutation), are
    all words of the first set similar to words of the second set?
    """
    d1, _ = __semi_distance_sets_of_words(
        set_words1, set_words2, list_prefixes, stemmer
    )
    return d1 == 0


def distance_sets_of_words(
    set_words1: list[str], set_words2: list[str], list_prefixes: list[str], stemmer
) -> int:
    """
    Given two sets of words (considered up to permutation), computes the distance between them.
    """
    d1, d2 = __semi_distance_sets_of_words(
        set_words1, set_words2, list_prefixes, stemmer
    )
    return d1 + d2


def new_stemmer(lang: str):
    """Returns a stemmer."""
    return nss.SnowballStemmer(lang)


def distance(
    notion1: str,
    notion2: str,
    list_prefixes: list[str],
    scopes_meaning: dict[str, list[list[str]]],
    lang: str,
) -> int:
    """
    Measures the distance between two notions, given a list of prefixes to ignore and
    a list of possible meaning for each scope.
    Args:
        notion1: first notion
        notion2: second notion
        list_prefixes: a list of prefixes that will be ignored
        scope_meaning: a dictionnary, assigning to every scope a list of
            its possible meanings, each possible meaning being a list of words
        lang: the identifier of some language (e.g. "english")

    Returns:
        The distance between notion1 and notion2.
    """
    kl1_words, sc1 = breakup_notion(notion1, lang)
    kl2_words, sc2 = breakup_notion(notion2, lang)
    stemmer = new_stemmer(lang)
    if sc1 != "" and sc2 != "" and sc1 != sc2:
        return cst.INFINITY
    if len(kl1_words) == 0 or len(kl2_words) == 0:
        # Can happen in the notion is a command
        return cst.INFINITY
    if sc1 == sc2:
        return distance_sets_of_words(kl1_words, kl2_words, list_prefixes, stemmer)
    if sc1 == "":
        kl1_words, sc1, kl2_words, sc2 = kl2_words, sc2, kl1_words, sc1
    # sc2 is empty and sc1 isn't
    # return the minimal distance obtained by replacing sc1 by one of its possible meanings
    dist = cst.INFINITY
    if sc1 in scopes_meaning:
        sc1_meaning = scopes_meaning[sc1]
    else:
        sc1_meaning = [[sc1]]
    for meaning in sc1_meaning:
        kl1_with_meaning = list(copy.copy(kl1_words))
        kl1_with_meaning.extend([w for w in meaning if w not in kl1_with_meaning])
        dist = min(
            dist,
            distance_sets_of_words(kl1_with_meaning, kl2_words, list_prefixes, stemmer),
        )
    return dist
