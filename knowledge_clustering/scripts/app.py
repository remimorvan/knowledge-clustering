import knowledge_clustering.diagnose as diag
import knowledge_clustering.kltex as kltex
import knowledge_clustering.clustering as clust
import knowledge_clustering.config as config
import knowledge_clustering.scope_meaning as sm
import knowledge_clustering.file_updater as fu


import click
from click_default_group import DefaultGroup
import nltk
import pkg_resources

ALPHA = 0
APP_NAME = "knowledge-clustering"

CONFIG_FILE = pkg_resources.resource_filename(
    "knowledge_clustering", "data/english.ini"
)


@click.group(cls=DefaultGroup, default='cluster', default_if_no_args=True)
def cli():
    """Automated notion clustering for the knowledge LaTeX package"""
    pass


@cli.command()
def init():
    """Downloads the required Nltk packages"""
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")


@cli.command()
@click.option(
    "--notion",
    "-n",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    help="File containing the notions that are already defined.",
    required=True
)
@click.option(
    "--diagnose",
    "-d",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Diagnose file produced by LaTeX.",
    required=True
)
@click.option(
    "--lang",
    "-l",
    default="en",
    type=click.Choice(["en"]),
    help="Language of your TeX document.",
)
@click.option(
    "--scope/--no-scope",
    " /-S",
    default=False,
    help="Print the scopes defined in the notion file and print \
the possible meaning of those scope inferred by Knowledge Clustering.",
)
@click.option(
    "--config-file",
    "-c",
    default=CONFIG_FILE,
    help=f"Specific configuration file. By default the following files is read {CONFIG_FILE}",
)
def cluster(notion, diagnose, scope, lang, config_file):
    """
    Edit a NOTION file using the knowledges present
    in a DIAGNOSE file.
    """
    with open(notion, "r") as f:
        document, known_knowledges = kltex.parse(f)

    list_prefixes = config.parse(config_file)

    scopes_meaning = sm.inferAllScopes(known_knowledges)

    if scope:
        sm.printScopes(scopes_meaning, print_meaning=True)

    unknown_knowledges = diag.parse(diagnose)

    if len(unknown_knowledges) == 0:
        return

    len_known_knowledges = len(known_knowledges)
    len_bags = [len(bag) for bag in known_knowledges]
    clust.clustering(
        known_knowledges,
        unknown_knowledges,
        ALPHA,
        list_prefixes,
        scopes_meaning,
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


if __name__ == "__main__":
    cli()
