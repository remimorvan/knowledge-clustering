"""
Launching knowledge commands (init, cluster, addquotes, anchor).
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

import os
import click
from click_default_group import DefaultGroup  # type: ignore
import nltk  # type: ignore
import pkg_resources

from knowledge_clustering import (
    add_anchor,
    add_quotes,
    diagnose,
    clustering,
    config,
    file_updater,
    scope_meaning,
)
from knowledge_clustering.knowledges import Knowledges
from knowledge_clustering.tex_document import TexDocument


_ALPHA = 0
# APP_NAME = "knowledge-clustering"

_CONFIG_FILENAME: dict[str, str] = {"en": "english.ini", "fr": "french.ini"}
_CONFIG_DIR: str = pkg_resources.resource_filename("knowledge_clustering", "data")
_CONFIG_FILE: dict[str, str] = dict()
for (lan, filename) in _CONFIG_FILENAME.items():
    _CONFIG_FILE[lan] = pkg_resources.resource_filename(
        "knowledge_clustering", f"data/{filename}"
    )
_NLTK_LANG: dict[str, str] = {"en": "english", "fr": "french"}


@click.group(cls=DefaultGroup, default="cluster", default_if_no_args=True)
def cli():
    """Automated notion clustering for the knowledge LaTeX package"""


@cli.command()
def init():
    """Downloads the required NLTK packages."""
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    os.system("python3 -m spacy download en_core_web_sm")
    os.system("python3 -m spacy download fr_core_news_sm")


@cli.command()
@click.option(
    "--knowledge",
    "-k",
    "kl_filename",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="File containing the knowledges that are already defined.",
    required=True,
)
@click.option(
    "--diagnose",
    "-d",
    "dg_filename",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Diagnose file produced by LaTeX.",
    required=True,
)
@click.option(
    "--lang",
    "-l",
    default="en",
    type=click.Choice(["en", "fr"]),
    help="Language of your TeX document.",
)
@click.option(
    "--scope/--no-scope",
    "-S/ ",
    default=False,
    help="Print the scopes defined in the knowledge file and print \
the possible meaning of those scope inferred by knowledge-clustering.",
)
@click.option(
    "--config-file",
    "-c",
    "config_filename",
    default=None,
    help=f"Specify the configuration file. By default the configuration file in the folder {_CONFIG_DIR} \
corresponding to your language is used.",
)
def cluster(
    kl_filename: str,
    dg_filename: str,
    scope: bool,
    lang: str,
    config_filename: None | str,
):
    """
    Defines, as a comment and in the knowledge file, all the knowledges occuring in the diagnose file.

    Args:
        kl_filename: the name of the knowledge file.
        dg_filename: the name of the diagnose file.
        scope: a boolean specifying whether the scopes meaning should be printed.
        lang: the langage of the document.
        config_filename: a configuration file, specifying prefixes to ignore.
    """
    kl = Knowledges(kl_filename)

    if config_filename is None:
        config_filename = _CONFIG_FILE[lang]

    list_prefixes = config.parse(config_filename)

    scopes_meaning = scope_meaning.infer_all_scopes(kl.get_all_bags(), _NLTK_LANG[lang])
    if scope:
        scope_meaning.print_scopes(scopes_meaning, print_meaning=True)

    unknown_knowledges = diagnose.parse(dg_filename)

    if len(unknown_knowledges) == 0:
        return

    # update `kl` using the clustering algorithm
    clustering.clustering(
        kl,
        unknown_knowledges,
        _ALPHA,
        list_prefixes,
        scopes_meaning,
        _NLTK_LANG[lang],
    )
    print(
        f"Found a solution by adding {len(kl.get_new_bags())} new bag"
        + ("s" if len(kl.get_new_bags()) >= 2 else "")
        + "."
    )
    kl.write_knowledges_in_file()


@cli.command()
@click.option(
    "--tex",
    "-t",
    "tex_filename",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="Your TeX file.",
    required=True,
)
@click.option(
    "--knowledge",
    "-k",
    "kl_filename",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="File containing the knowledges that are already defined.",
    required=True,
)
@click.option(
    "--print",
    "-p",
    "print_line",
    type=int,
    default=1,
    help="When finding a match, number of lines (preceding the match) that are printed in the prompt to the user.",
)
def addquotes(tex_filename: str, kl_filename: str, print_line: int):
    """
    Finds knowledges defined in the knowledge file that appear in tex file without quote
    symbols. Proposes to add quotes around them.

    Args:
        tex_filename: the name of the tex file.
        kl_filename: the name of the knowledge file.
        print_line: an integer specifying how many lines of the tex file should be printed.
    """
    tex_hash = file_updater.hash_file(tex_filename)
    with open(tex_filename, "r", encoding="utf-8") as f:
        tex_doc = TexDocument(f.read())
    kl = Knowledges(kl_filename)
    tex_document_new, new_knowledges = add_quotes.quote_maximal_substrings(
        tex_doc, kl, print_line
    )
    with file_updater.AtomicUpdate(tex_filename, original_hash=tex_hash) as f:
        f.write(tex_document_new)
    for known_kl, new_kl in new_knowledges:
        kl.define_synonym_of(new_kl, known_kl)
    kl.write_knowledges_in_file(nocomment=True)


@cli.command()
@click.option(
    "--tex",
    "-t",
    "tex_filename",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="Your TeX file.",
    required=True,
)
@click.option(
    "--space",
    "-s",
    type=int,
    default=150,
    help="Number of characters tolerated between an anchor point and the introduction \
        of a knowledge. (Default value: 150)",
)
def anchor(tex_filename, space):
    """
    Prints warning when a knowledge is introduced but is not preceded by an anchor point.

    Args:
        tex_filename: the name of the tex file.
        space: an integer specifying the maximal number of characters allowed between the
            introduction of a knowledge and an anchor point.
    """
    with open(tex_filename, "r", encoding="utf-8") as f:
        tex_doc = TexDocument(f.read())
    add_anchor.missing_anchor(tex_doc, space)


if __name__ == "__main__":
    cli()
