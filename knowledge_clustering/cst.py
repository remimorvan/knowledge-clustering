"""
Constants used throughout knowledge-clustering.
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

from pathlib import Path
from importlib import resources

ALPHA = 0

CONFIG_FILENAME: dict[str, str] = {"en": "english.ini", "fr": "french.ini"}
ref = resources.files("knowledge_clustering") / "data"
with resources.as_file(ref) as path:
    CONFIG_DIR: Path = path
CONFIG_FILE: dict[str, Path] = dict()
for lan, filename in CONFIG_FILENAME.items():
    ref_file = resources.files("knowledge_clustering") / f"data/{filename}"
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
IGNORE_CHAR_BACKSLASH = [
    # LaTeX accents defined using non-alphanumerical commands
    "\\`",
    "\\'",
    "\\^",
    '\\"',
    "\\~",
    "\\=",
    "\\.",
    "\\-",  # Hyphen
]
IGNORE_CHAR_NO_BACKSLASH = ["{", "}"]
SPACE_CHAR = ["~"]

DISCARD_LINE = "%%%%% NEW KNOWLEDGES "

TIMEOUT_REQUEST: float = (
    0.25  # Timeout to resquest the latest version
    # of knowledge-clustering (in seconds)
)
