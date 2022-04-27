# Knowledge-Clustering

[![PyPI](https://img.shields.io/pypi/v/knowledge-clustering.svg)](https://pypi.python.org/pypi/knowledge-clustering)

Clustering notions for the [knowledge LaTeX package](https://ctan.org/pkg/knowledge).
Maintained by Rémi Morvan, Thomas Colcombet and Aliaume Lopez.

## Principle

The goal of **Knowledge-Clustering** is to help the user write a LaTeX document with
the [knowledge package](https://ctan.org/pkg/knowledge).
It has two features:

  - **Clustering**: provide suggestions to the user of what notions should be grouped together.
  - **Add quotes**: find where you might have missed some quotes in your document.

## Installation

To install (or upgrade) **Knowledge-Clustering**, run

    pip3 install --upgrade knowledge-clustering

and then

    knowledge init

## Clustering notions 

### Syntax

```
Usage: knowledge cluster [OPTIONS]

  Edit a NOTION file using the knowledges present in a DIAGNOSE file.

Options:
  -n, --notion FILE         File containing the notions that are already
                            defined.  [required]
  -d, --diagnose FILE       Diagnose file produced by LaTeX.  [required]
  -l, --lang [en|fr]        Language of your TeX document.
  -S, --scope / --no-scope  Print the scopes defined in the notion file and
                            print the possible meaning of those scope inferred
                            by Knowledge Clustering.
  -c, --config-file TEXT    Specify the configuration file. By default the
                            configuration file in the folder
                            /Users/rmorvan/GDrive/Code/knowledge-
                            clustering/knowledge_clustering/data corresponding
                            to your language is used.
  --help                    Show this message and exit.
```

### Example

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

    knowledge cluster -n small.tex -d small.diagnose

your file `small.diagnose` is left unchanged
but `small.tex` is updated with comments.

The `cluster` command is optional: you can also write `knowledge -n small.tex -d small.diagnose`.

![After running Knowledge-Clustering, the five undefined knowledges are included in the `small.tex` file as comments.](img/small-after.png "Files `small.tex` and `small.diagnose` after running Knowledge-Clustering`")

Now you simply have to check that the recommandations of **Knowledge-Clustering** are
correct, and uncomment those lines.

## Adding quotes

```
Usage: knowledge addquotes [OPTIONS]

  Finds knowledges defined in NOTION that appear in TEX without quote symbols.
  Proposes to add (or add, if the force option is enabled) quotes around them.

Options:
  -t, --tex FILE     Your TeX file.  [required]
  -n, --notion FILE  File containing the notions that are already defined.
                     [required]
  -F, --force        Don't ask the user and always add quotes if a match is
                     found.
  --help             Show this message and exit.
```

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
