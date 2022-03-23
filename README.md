# Knowledge-Clustering

[![PyPI](https://img.shields.io/pypi/v/knowledge-clustering.svg)](https://pypi.python.org/pypi/knowledge-clustering)

Clustering notions for the [knowledge LaTeX package](https://ctan.org/pkg/knowledge).
Maintained by Rémi Morvan, Thomas Colcombet and Aliaume Lopez.

## Principle

The goal of **Knowledge-Clustering** is, when using the [knowledge package](https://ctan.org/pkg/knowledge) to automatically provide suggestions to the user of what notions should be grouped together.

## Installation

To install (or upgrade) **Knowledge-Clustering**, run

    python3 -m pip install --upgrade knowledge-clustering

and then

    knowledge init

## Syntax

```
Usage: knowledge cluster [OPTIONS] NOTION DIAGNOSE

  Edit a NOTION file using the knowledges present in a DIAGNOSE file.

  NOTION:   File containing the diagnose file produced by TeX.

  DIAGNOSE: File containing the knowledges/notions defined by the user.

Options:
  -l, --lang [en]           Language of your TeX document.
  --scope / -S, --no-scope  Print the scopes defined in the notion file and
                            print     the possible meaning of those scope
                            inferred by Knowledge Clustering.
  -c, --config-file TEXT    Specific configuration file. By default the
                            following files is read
                            $APP_PATH/knowledge_clustering/data/english.txt
  --help                    Show this message and exit.
```

## Example

Example files can be found in the `examples/` folder.

While writing some document, you have defined some knowledges in a file called `small.tex` (distinct
from your main `LaTeX`).
You continued writing your `LaTeX` document (not provided in the `examples/` folder)
for some time, and used some knowledges that were undefined.
When compiling, `LaTeX` and the [`knowledge package`](https://ctan.org/pkg/knowledge) gives you a warning
and writes in a `.diagnose` file some information explaining what went wrong. This `.diagnose` file contains
a section called "Undefined knowledges" containing all knowledges used in your main `LaTeX` file but not
defined in `small.tex`. We reproduced this section
in the `small.diagnose` file.

![Screenshot of the `small.tex` and `small.diagnose` files before running Knowledge-Clustering. `small.tex` contains four knowledges, while `small.diagnose` contains five undefined knowledges.](img/small-before.png "Files `small.tex` and `small.diagnose` before running Knowledge-Clustering")

Normally, you would add every undefined knowledge, one after the other, in your
`small.tex`. This is quite burdensome and can
largely be automated: you don't need a PhD to
understand that "word" and "words" are similar words. This is precisely what **Knowledge-Clustering** does: after running

    knowledge -n small.tex -d small.diagnose

your file `small.diagnose` is left unchanged
but `small.tex` is updated with comments.

![After running Knowledge-Clustering, the five undefined knowledges are included in the `small.tex` file as comments.](img/small-after.png "Files `small.tex` and `small.diagnose` after running Knowledge-Clustering`")

Now you simply have to check that the recommandations of **Knowledge-Clustering** are
correct, and uncomment those lines.

## Devel using virtualenv

Using virtualenv and the `--editable` option from `pip3` allows for an easy
setup of a development environment that will match a future user install without
the hassle.

For bash and Zsh users

```bash
virtualenv -p python3 kw-devel
source ./kw-devel/bin/activate
pip3 install --editable .
```

For fish users

```fish
virtualenv -p python3 kw-devel
source ./kw-devel/bin/activate.fish
pip3 install --editable .
```

## FAQ

- When running `knowledge`, I obtain a long message error indicating "Resource punkt not found."

  **Solution**: run `knowledge init`.

- My shell doesn't autocomplete the command `knowledge`.

  **Solution**: depending on whether you use `zsh` or `bash` write

       eval "`pip completion --<shellname>`"

  (where `<shellname>` is either `zsh` or `bash`)
  in your `.zshrc` (or `.bashrc`) file and then,
  either lunch a new terminal or run `source ~/.zshrc`
  (or `source ~/.bashrc`).
