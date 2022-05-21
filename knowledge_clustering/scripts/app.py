import knowledge_clustering.diagnose as diag
import knowledge_clustering.kltex as kltex
import knowledge_clustering.clustering as clust
import knowledge_clustering.config as config
import knowledge_clustering.scope_meaning as sm
import knowledge_clustering.file_updater as fu
import knowledge_clustering.add_quotes as quotes


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
    os.system("python3 -m spacy download en")
    os.system("python3 -m spacy download fr")


@cli.command()
@click.option(
    "--notion",
    "-n",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="File containing the notions that are already defined.",
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
    help="Print the scopes defined in the notion file and print \
the possible meaning of those scope inferred by Knowledge Clustering.",
)
@click.option(
    "--config-file",
    "-c",
    default=None,
    help=f"Specify the configuration file. By default the configuration file in the folder {CONFIG_DIR} \
corresponding to your language is used.",
)
def cluster(notion, diagnose, scope, lang, config_file):
    """
    Edit a NOTION file using the knowledges present
    in a DIAGNOSE file.
    """
    with open(notion, "r") as f:
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
    print(f"Found a solution by adding {len(new_knowledges)} new bag(s).")

    with fu.AtomicUpdate(notion) as f:
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
    "--notion",
    "-n",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="File containing the notions that are already defined.",
    required=True,
)
@click.option(
    "--force",
    "-F",
    is_flag=True,
    help="Don't ask the user and always add quotes if a match is found.",
)
def addquotes(tex, notion, force):
    """
    Finds knowledges defined in NOTION that appear in TEX without quote symbols.
    Proposes to add (or add, if the force option is enabled) quotes around them.
    """
    with open(tex, "r") as f:
        tex_document = f.read()
    with open(notion, "r") as f:
        _, known_knowledges = kltex.parse(f)
    known_knowledges = [kl for bag in known_knowledges for kl in bag]
    tex_document_new = quotes.quote_maximal_substrings(
        tex_document, known_knowledges, not force, False, 4
    )
    with fu.AtomicUpdate(tex) as f:
        f.write(tex_document_new)


if __name__ == "__main__":
    cli()
