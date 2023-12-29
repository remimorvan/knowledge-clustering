"""
Launching knowledge commands (init, cluster, addquotes, anchor).
"""

from __future__ import annotations  # Support of `|` for type union in Python 3.9
from pathlib import Path

import os
import sys
import click
from click_default_group import DefaultGroup  # type: ignore
import nltk  # type: ignore

from knowledge_clustering import (
    add_anchor,
    add_quotes,
    clustering,
    cst,
    _version,
    autofinder,
)
from knowledge_clustering.check_update import check_update
from knowledge_clustering.misc import add_red, add_bold


# https://stackoverflow.com/a/67324391/19340201
class AliasedGroup(DefaultGroup):
    """Group where `AP` is a synonym for `anchor`."""

    def get_command(self, ctx, cmd_name):
        if cmd_name in ["anchor", "AP"]:
            return DefaultGroup.get_command(self, ctx, "anchor")
        return DefaultGroup.get_command(self, ctx, cmd_name)


@click.group(cls=AliasedGroup, default="cluster", default_if_no_args=True)
@click.version_option(_version.VERSION)
def cli():
    """Automated notion clustering for the knowledge LaTeX package"""


@cli.command()
def init():
    """Downloads the required NLTK packages."""
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    os.system(sys.executable + " -m spacy download en_core_web_sm")
    os.system(sys.executable + " -m spacy download fr_core_news_sm")


@cli.command()
@click.option(
    "--knowledge",
    "-k",
    "kl_filename",
    multiple=True,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="File containing the knowledges that are already defined. \
Multiple files are allowed; new knowledges will be written in the last one. \
If the option is not specified, all .kl file in the current directory (and subdirectory, \
recursively) will be taken. If there are multiple files, exactly one of them must end \
with `default.kl`.",
    required=False,
)
@click.option(
    "--diagnose",
    "-d",
    "dg_filename",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Diagnose file produced by LaTeX. If the option is not specified, the unique \
.diagnose file in the current directory (and subdirectory, recursively) is taken instead.",
    required=False,
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
    "--no-update/--update",
    "-N/ ",
    "noupdate",
    default=False,
    help="Don't look on PyPI if a newer version of knowledge-clustering is available.",
)
@click.option(
    "--config-file",
    "-c",
    "config_filename",
    default=None,
    help=f"Specify the configuration file. By default the configuration file \
in the folder {cst.CONFIG_DIR} corresponding to your language is used.",
)
def cluster(
    kl_filename: tuple[str],
    dg_filename: str,
    lang: str,
    scope: bool,
    noupdate: bool,
    config_filename: None | str,
):
    """
    Defines, as a comment and in the knowledge files, all the knowledges occuring in the file.
    """
    try:
        if not dg_filename:
            dg_filename = autofinder.get_unique_diagnose_file(Path("."))
        kl_filename = list(kl_filename)
        if not kl_filename:
            kl_filename = autofinder.get_knowledge_files(Path("."))
        clustering.app(kl_filename, dg_filename, scope, lang, config_filename)
        if not noupdate:
            check_update()
    except (autofinder.NoFile, autofinder.TooManyFiles) as e:
        print(add_bold(add_red("\n[Error] ")) + e.args[0])


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
    multiple=True,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="File containing the knowledges that are already defined. \
Multiple files are allowed; new knowledges will be written in the last one. \
If the option is not specified, all .kl file in the current directory (and subdirectory, \
recursively) will be taken. If there are multiple files, exactly one of them must end \
with `default.kl`.",
    required=False,
)
@click.option(
    "--print",
    "-p",
    "print_line",
    type=int,
    default=1,
    help="When finding a match, number of lines (preceding the match) that are printed \
in the prompt to the user.",
)
@click.option(
    "--no-update/--update",
    "-N/ ",
    "noupdate",
    default=False,
)
def addquotes(tex_filename: str, kl_filename: str, print_line: int, noupdate: bool):
    """
    Finds knowledges defined in the knowledge files that appear in tex file without quote
    symbols. Proposes to add quotes around them.
    """
    try:
        kl_filename = list(kl_filename)
        if not kl_filename:
            kl_filename = autofinder.get_knowledge_files(Path("."))
        add_quotes.app(tex_filename, kl_filename, print_line)
        if not noupdate:
            check_update()
    except (autofinder.NoFile, autofinder.TooManyFiles) as e:
        print(add_bold(add_red("\n[Error] ")) + e.args[0])


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
@click.option(
    "--no-update/--update",
    "-N/ ",
    "noupdate",
    default=False,
)
def anchor(tex_filename: str, space: int, noupdate: bool):
    """
    Prints warning when a knowledge is introduced but is not preceded by an anchor point.
    """
    add_anchor.app(tex_filename, space)
    if not noupdate:
        check_update()


if __name__ == "__main__":
    cli()
