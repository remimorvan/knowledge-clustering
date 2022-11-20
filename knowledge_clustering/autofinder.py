from __future__ import annotations

import os


def autofinder():
    """Automatically finds
    suitable .diagnose and .notion
    files in the current working directory
    and yields them
    """

    for root, dirs, files in os.walk("."):
        for file in files:
            if os.path.basename(file).endswith(".diagnose"):
                yield ("notion", file)
            elif os.path.basename(file).endswith(".knowledge") or os.path.basename(
                file
            ).endswith(".kw"):
                yield ("knowledge", file)
