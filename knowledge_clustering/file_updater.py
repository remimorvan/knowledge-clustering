#
# Allow to atomically update a
# file by writing to a temporary
# file and comparing hashes.
# In case of conflicting uses,
# the user has to manually merge
# and a prompt is offered using click.
#

from __future__ import annotations

import hashlib
import tempfile
import os
import click


def hash_file(filepath: str):
    """
    Compute a hash of the content of the
    given filepath
    """
    with open(filepath, "rb") as f:
        file_hash = hashlib.blake2b()
        chunk: bytes = f.read(8192)
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

    def __init__(self, filename, original_hash=None):
        self.filename: str = filename
        self.hash = hash_file(filename)
        self.ctx = tempfile.NamedTemporaryFile(mode="w", dir=os.getcwd(), delete=False)
        self.tmp = None
        if (
            original_hash is not None
            and original_hash.hexdigest() != self.hash.hexdigest()
        ):
            click.confirm(
                f"File {self.filename} has been modified during the run of the program, erase anyway?",
                default=None,
                abort=True,
                prompt_suffix=": ",
                show_default=True,
                err=False,
            )

    def __enter__(self):
        self.tmp = self.ctx.__enter__()
        return self.tmp

    def __exit__(self, type, value, traceback):
        nh = hash_file(self.filename)
        if self.tmp is not None:
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
