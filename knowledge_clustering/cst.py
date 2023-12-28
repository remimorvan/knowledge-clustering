"""
Constants used throughout knowledge-clustering.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

from importlib import resources

ALPHA = 0

CONFIG_FILENAME: dict[str, str] = {"en": "english.ini", "fr": "french.ini"}
ref = resources.files('knowledge_clustering') / 'data'
with resources.as_file(ref) as path:
    CONFIG_DIR: str = path
CONFIG_FILE: dict[str, str] = dict()
for lan, filename in CONFIG_FILENAME.items():
    ref_file =  resources.files('knowledge_clustering') / f"data/{filename}"
    with resources.as_file(ref_file) as path_file:
        CONFIG_FILE[lan] = path_file
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
SPACE_CHAR = ["~"]

DISCARD_LINE = "%%%%% NEW KNOWLEDGES "

BEGIN_EMPH: str = "\033[1m\033[95m"
BEGIN_EMPH_ALT: str = "\033[1m\033[92m"
BEGIN_EMPH_BOLD: str = "\033[1m"
BEGIN_RED: str = "\033[31m"
BEGIN_ORANGE: str = "\033[33m"
BEGIN_GREEN: str = "\033[32m"
END_EMPH: str = "\033[0m"

TIMEOUT_REQUEST: float = (
    0.2  # Timeout to resquest the latest version
    # of knowledge-clustering (in seconds)
)
