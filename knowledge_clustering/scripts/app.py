import knowledge_clustering.diagnose as diag
import knowledge_clustering.kltex as kltex
import knowledge_clustering.clustering as clust
import knowledge_clustering.config as config
import knowledge_clustering.scope_meaning as sm
import knowledge_clustering.file_updater as fu
import knowledge_clustering.add_quotes as quotes
import knowledge_clustering.add_AP as ap


import click
from click_default_group import DefaultGroup
import nltk
import pkg_resources
import os

ALPHA = 0
APP_NAME = "knowledge-clustering"

CONFIG_FILENAME = {"en": "english.ini", "fr": "french.ini"}
CONFIG_DIR = pkg_resources.resource_filename("knowledge_clustering", "data")
CONFIG_FILE = dict()
for lang in CONFIG_FILENAME.keys():
    CONFIG_FILE[lang] = pkg_resources.resource_filename(
        "knowledge_clustering", f"data/{CONFIG_FILENAME[lang]}"
    )
NLTK_LANG = {"en": "english", "fr": "french"}


@click.group(cls=DefaultGroup, default="cluster", default_if_no_args=True)
def cli():
    """Automated notion clustering for the knowledge LaTeX package"""
    pass


@cli.command()
def init():
    """Downloads the required Nltk packages"""
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    os.system("python3 -m spacy download en_core_web_sm")
    os.system("python3 -m spacy download fr_core_news_sm")


@cli.command()
@click.option(
    "--knowledge",
    "-k",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="File containing the knowledges that are already defined.",
    required=True,
)
@click.option(
    "--diagnose",
    "-d",
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
    default=None,
    help=f"Specify the configuration file. By default the configuration file in the folder {CONFIG_DIR} \
corresponding to your language is used.",
)
def cluster(knowledge, diagnose, scope, lang, config_file):
    """
    Edit a KNOWLEDGE file using the knowledges present
    in a DIAGNOSE file.
    """
    with open(knowledge, "r") as f:
        document, known_knowledges = kltex.parse(f)

    if config_file == None:
        config_file = CONFIG_FILE[lang]

    list_prefixes = config.parse(config_file)

    scopes_meaning = sm.inferAllScopes(known_knowledges, NLTK_LANG[lang])
    if scope:
        sm.printScopes(scopes_meaning, print_meaning=True)

    unknown_knowledges = diag.parse(diagnose)

    if len(unknown_knowledges) == 0:
        return

    len_known_knowledges = len(known_knowledges)
    len_bags = [len(bag) for bag in known_knowledges]
    # update known_knowledges using the clustering algorithm
    clust.clustering(
        known_knowledges,
        unknown_knowledges,
        ALPHA,
        list_prefixes,
        scopes_meaning,
        NLTK_LANG[lang],
    )
    # Compute updated_knowledges and new_knowledges
    new_knowledges = known_knowledges[len_known_knowledges:]
    updated_knowledges = [
        known_knowledges[bag_id][len_bags[bag_id] :]
        for bag_id in range(len_known_knowledges)
    ]
    print(
        f"Found a solution by adding {len(new_knowledges)} new knowledge"
        + ("s" if len(new_knowledges) >= 2 else "")
        + "."
    )

    with fu.AtomicUpdate(knowledge) as f:
        kltex.writeDocument(f, document, updated_knowledges, new_knowledges)


@cli.command()
@click.option(
    "--tex",
    "-t",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="Your TeX file.",
    required=True,
)
@click.option(
    "--knowledge",
    "-k",
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
def addquotes(tex, knowledge, print_line):
    """
    Finds knowledges defined in KNOWLEDGE that appear in TEX without quote
    symbols. Proposes to add quotes around them.
    """
    with open(tex, "r") as f:
        tex_document = f.read()
    with open(knowledge, "r") as f:
        kl_document, known_knowledges = kltex.parse(f)
    known_knowledges_flat = [kl for bag in known_knowledges for kl in bag]
    tex_document_new, new_knowledges = quotes.quote_maximal_substrings(
        tex_document, known_knowledges_flat, print_line, size_tab=4
    )
    with fu.AtomicUpdate(tex) as f:
        f.write(tex_document_new)
    updated_knowledges = [
        [new_kl for (def_kl, new_kl) in new_knowledges if def_kl in bag]
        for bag in known_knowledges
    ]
    if updated_knowledges != []:
        with fu.AtomicUpdate(knowledge) as f:
            kltex.writeDocument(f, kl_document, updated_knowledges, [], nocomment=True)


@cli.command()
@click.option(
    "--tex",
    "-t",
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
    help="Number of characters tolerated between an anchor point and the introduction of a knowledge. (Default value: 150)",
)
def anchor(tex, space):
    """
    Prints warning when a knowledge is introduced but
    is not preceded by an anchor point.
    """
    with open(tex, "r") as f:
        tex_document = f.read()
    ap.missing_AP(tex_document, space, size_tab=4)


if __name__ == "__main__":
    cli()
