"""
Checks if there is a newer version of knowledge-clustering available on PyPI.
"""

import requests
from pip._vendor.rich.markup import escape
from pip._internal.utils.entrypoints import get_best_invocation_for_this_pip

from knowledge_clustering import _version
from knowledge_clustering.misc import emph_alt, print_red, print_green
from knowledge_clustering.cst import TIMEOUT_REQUEST


def check_update() -> None:
    """
    Checks if an update is available, and if so, prints a message in
    the string pointer given as input.
    """
    # From https://stackoverflow.com/a/62571316/19340201
    try:
        package = "knowledge-clustering"
        response = requests.get(
            f"https://pypi.org/pypi/{package}/json", timeout=TIMEOUT_REQUEST
        )
        latest_version: str = response.json()["info"]["version"]
        is_available: bool = latest_version != _version.VERSION
    except requests.exceptions.RequestException:
        is_available = False
        latest_version = ""
    # If available, print message
    msg = ""
    if is_available:
        msg += (
            "\n"
            + emph_alt("[notice]")
            + " A new release of knowledge-clustering is available: "
            + print_red(_version.VERSION)
            + " -> "
            + print_green(latest_version)
        )
        msg += (
            "\n"
            + emph_alt("[notice]")
            + " To update, run: "
            + print_green(
                escape(get_best_invocation_for_this_pip())
                + " install --upgrade knowledge-clustering"
            )
        )
    print(msg)
