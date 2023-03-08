"""
Launching knowledge commands (init, cluster, addquotes, anchor).
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

import os
import click
from click_default_group import DefaultGroup  # type: ignore
import nltk  # type: ignore

from knowledge_clustering import add_anchor, add_quotes, clustering, cst, _version


@click.group(cls=DefaultGroup, default="cluster", default_if_no_args=True)
@click.version_option(_version.VERSION)
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
    help=f"Specify the configuration file. By default the configuration file in the folder {cst.CONFIG_DIR} \
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
    """
    clustering.app(kl_filename, dg_filename, scope, lang, config_filename)


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
    """
    return add_quotes.app(tex_filename, kl_filename, print_line)


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
    default=200,
    help="Number of characters tolerated between an anchor point and the introduction \
of a knowledge. (Default value: 200)",
)
def anchor(tex_filename: str, space: int):
    """
    Prints warning when a knowledge is introduced but is not preceded by an anchor point.
    """
    return add_anchor.app(tex_filename, space)


if __name__ == "__main__":
    cli()
