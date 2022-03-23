import knowledge_clustering.diagnose as diag
import knowledge_clustering.kltex as kltex
import knowledge_clustering.clustering as clust
import knowledge_clustering.config as config
import knowledge_clustering.scope_meaning as sm


import hashlib
import tempfile
import click
import os
import nltk
import pkg_resources

ALPHA = 0
APP_NAME = "knowledge-clustering"

CONFIG_FILE = pkg_resources.resource_filename(
    "knowledge_clustering", "data/english.txt"
)


def hash_file(filepath):
    with open(filepath, "rb") as f:
        file_hash = hashlib.blake2b()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
        return file_hash


class AtomicUpdate:
    """
    A small class using a temporary file to ensure that we have
    properly replaced the content. Prompts the user if we detect
    a change in the hash of the file given as input.
    """

    def __init__(self, filename):
        self.filename = filename
        self.hash = hash_file(filename)
        self.ctx = tempfile.NamedTemporaryFile(mode="w", dir=os.getcwd(), delete=False)
        self.tmp = None

    def __enter__(self):
        self.tmp = self.ctx.__enter__()
        return self.tmp

    def __exit__(self, type, value, traceback):
        nh = hash_file(self.filename)
        if nh.hexdigest() != self.hash.hexdigest():
            print(f"{nh.hexdigest()} ≠ {self.hash.hexdigest()}")
            b = click.confirm(
                f"File {self.filename} has been modified\
                during the run of \
                the program, erase anyway?",
                default=None,
                abort=False,
                prompt_suffix=": ",
                show_default=True,
                err=False,
            )
            if b is False:
                print(f"Temporary file accessible at {self.tmp.name}")
                return self.ctx.__exit__(type, value, traceback)
        os.replace(self.tmp.name, self.filename)
        return self.ctx.__exit__(type, value, traceback)


@click.group()
def cli():
    """Automated notion clustering for the knowledge LaTeX package"""
    pass


@cli.command()
def init():
    """Downloads the required Nltk packages"""
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")


@cli.command()
@click.argument(
    "notion",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, readable=True
    ),
)
@click.argument(
    "diagnose",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
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

    NOTION:   File containing the diagnose file produced by TeX.

    DIAGNOSE: File containing the knowledges/notions defined by the user.
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

    with AtomicUpdate(notion) as f:
        kltex.writeDocument(f, document, updated_knowledges, new_knowledges)


if __name__ == "__main__":
    cli()
