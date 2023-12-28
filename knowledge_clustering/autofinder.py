"""Automatically finds files in the current directory."""

from __future__ import annotations  # Support of `|` for type union in Python 3.9

from pathlib import Path


class NoFile(Exception):
    """When no file is found."""


class TooManyFiles(Exception):
    """When too many files are found compared to what was expected."""


def find_ext(dr: Path, ext: str) -> list[Path]:
    """
    Lists all files present in a directory (and its subdirectory, recursively)
    that ends with some given extension.
    """
    return list(dr.glob(f"**/*.{ext}"))


def get_unique_diagnose_file(dr: Path) -> Path:
    """
    Returns the unique .diagnose file present in a directory (and its subdirectory, recursively),
    fails otherwise.
    """
    dg_files = find_ext(dr, "diagnose")
    if len(dg_files) == 0:
        raise NoFile("No .diagnose file present in the directory.")
    if len(dg_files) > 1:
        raise TooManyFiles(
            f"Multiple .diagnose files present in the directory: \
f{dg_files[0]} and {dg_files[1]}."
        )
    return dg_files[0]


def get_knowledge_files(dr: Path) -> list[Path]:
    """
    Returns the list of all .kl files present in a directory (and its subdirectory, recursively).
    Fails if there is no .kl file. Fails if there are multiple .kl file, but not a unique one
    ending with `default.kl`.
    """
    kl_files = find_ext(dr, "kl")
    if len(kl_files) == 0:
        raise NoFile("No .kl file present in the directory.")
    if len(kl_files) == 1:
        return kl_files
    list_default = []
    for i, p in enumerate(kl_files):
        if str(p).endswith("default.kl"):
            list_default.append(i)
    if len(list_default) == 0:
        raise NoFile("No file ending with `default.kl` present in the directory.")
    if len(list_default) > 1:
        raise TooManyFiles(
            f"Multiple files ending with `default.kl` present in the directory: \
f{kl_files[list_default[0]]} and {kl_files[list_default[1]]}."
        )
    idx_default = list_default[0]
    idx_last = len(kl_files) - 1
    kl_files[idx_last], kl_files[idx_default] = (
        kl_files[idx_default],
        kl_files[idx_last],
    )
    return kl_files
