"""
Constants used throughout knowledge-clustering.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

import pkg_resources

ALPHA = 0

CONFIG_FILENAME: dict[str, str] = {"en": "english.ini", "fr": "french.ini"}
CONFIG_DIR: str = pkg_resources.resource_filename("knowledge_clustering", "data")
CONFIG_FILE: dict[str, str] = dict()
for (lan, filename) in CONFIG_FILENAME.items():
    CONFIG_FILE[lan] = pkg_resources.resource_filename(
        "knowledge_clustering", f"data/{filename}"
    )
NLTK_LANG: dict[str, str] = {"en": "english", "fr": "french"}

INTRO_DELIMITERS: list[tuple[str, str]] = [
    ('""', '""'),
    ("\\intro{", "}"),
    ("\\reintro{", "}"),
    ("\\phantomintro{", "}"),
    ("\\intro[", "]"),
    ("\\reintro[", "]"),
    ("\\phantomintro[", "]"),
]
AP_STRING: list[str] = ["\\AP", "\\itemAP"]

KL_DELIMITERS: list[tuple[str, str]] = [
    ('"', '"'),
    ('"', "@"),
    ("@", '"'),
    ("@", "@"),
    ("\\kl{", "}"),
    ("\\intro{", "}"),
    ("\\reintro{", "}"),
    ("\\phantomintro{", "}"),
    ("\\kl[", "]"),
    ("\\intro[", "]"),
    ("\\reintro[", "]"),
    ("\\phantomintro[", "]"),
]

SEPARATION_HEADING_KL_BLOCK = "************************"

IMPORTANT_POS = [
    "CD",
    "JJ",
    "JJR",
    "JJS",
    "NN",
    "NNP",
    "NNS",
    "PDT",
    "RB",
    "RBR",
    "RBS",
    "VB",
    "VBD",
    "VBG",
    "VBN",
    "VBP",
    "VBZ",
]
IGNORE_SUFFIXES = ["", "s"]
INFINITY = 10000
LATEX_ACCENTS = [
    "\\`",
    "\\'",
    "\\^",
    '\\"',
    "\\~",
    "\\=",
    "\\.",
]  # LaTeX accents defined using non-alphanumerical commands
IGNORE_CHAR = ["\\-", "{", "}"]

DISCARD_LINE = "%%%%% NEW KNOWLEDGES "

BEGIN_EMPH: str = "\033[1m\033[95m"
BEGIN_EMPH_ALT: str = "\033[1m\033[92m"
BEGIN_EMPH_BOLD: str = "\033[1m"
END_EMPH: str = "\033[0m"
