# knowledge-clustering

[![PyPI](https://img.shields.io/pypi/v/knowledge-clustering.svg)](https://pypi.python.org/pypi/knowledge-clustering)

Clustering notions for the [knowledge LaTeX package](https://ctan.org/pkg/knowledge).
Maintained by Rémi Morvan, Thomas Colcombet and Aliaume Lopez.
A tutorial on how to use `knowledge-clustering` can be found [here](https://github.com/remimorvan/knowledge-examples).

## Principle

The goal of `knowledge-clustering` is to help the user write a LaTeX document with
the [knowledge package](https://ctan.org/pkg/knowledge).
It has three features:

  - **Clustering**: provide suggestions to the user of what notions should be grouped together.
  - **Add quotes**: find where you might have missed some quotes in your document.
  - **Anchor points**: find where you might have missed anchor points in your document.

The **clustering** algorithm is meant to be use while writing your document, while the last two tools
should be used when your document is (nearly) ready to be published, to check if everything is right.

## Installation

To install (or upgrade) `knowledge-clustering`, run

    pip3 install --upgrade knowledge-clustering

and then

    knowledge init

## Clustering notions 

### Syntax

```
Usage: knowledge cluster [OPTIONS]

  Edit a NOTION file using the knowledges present in a DIAGNOSE file.

Options:
  -k, --knowledge FILE      File containing the knowledges that are already
                            defined.  [required]
  -d, --diagnose FILE       Diagnose file produced by LaTeX.  [required]
  -l, --lang [en|fr]        Language of your TeX document.
  -S, --scope / --no-scope  Print the scopes defined in the notion file and
                            print the possible meaning of those scope inferred
                            by knowledge-clustering.
  -c, --config-file TEXT    Specify the configuration file. By default the
                            configuration file in the folder
                            <knowledge-clustering-installation-
                            folder>/knowledge_clustering/data/ corresponding
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

![Screenshot of the `small.tex` and `small.diagnose` files before running knowledge-clustering. `small.tex` contains four knowledges, while `small.diagnose` contains five undefined knowledges.](img/small-before.png "Files `small.tex` and `small.diagnose` before running knowledge-clustering")

Normally, you would add every undefined knowledge, one after the other, in your
`small.tex`. This is quite burdensome and can
largely be automated. This is precisely what `knowledge-clustering` does: after running

    knowledge cluster -k small.tex -d small.diagnose

your file `small.diagnose` is left unchanged
but `small.tex` is updated with comments.

The `cluster` command is optional: you can also write `knowledge -k small.tex -d small.diagnose`.

![After running knowledge-clustering, the five undefined knowledges are included in the `small.tex` file as comments.](img/small-after.png "Files `small.tex` and `small.diagnose` after running knowledge-clustering`")

Now you simply have to check that the recommandations of `knowledge-clustering` are
correct, and uncomment those lines.

## Adding quotes

```
Usage: knowledge addquotes [OPTIONS]

  Finds knowledges defined in KNOWLEDGE that appear in TEX without quote
  symbols. Proposes to add quotes around them.

Options:
  -t, --tex FILE        Your TeX file.  [required]
  -k, --knowledge FILE  File containing the knowledges that are already
                        defined.  [required]
  -p, --print INTEGER   When finding a match, number of lines (preceding the
                        match) that are printed in the prompt to the user.
  --help                Show this message and exit.
```

After running 

    knowledge addquotes -t mydocument.tex -k knowledges.tex

your prompt will propose to add quotes around defined knowledges,
and to define synonyms of knowledges that occur in your TeX file. For instance, if
"algorithm" is a defined knowledge and "algorithms" occurs in your TeX file, then
it will propose to you to define "algorithms" as a synonym of the knowledge "algorithm",
and to add a pair of quotes around the string "algorithms" that occurs in your TeX file.

Whenever the algorithm finds a match for a knowledge, it will print the line of
the document where it found the match, and emphasize the string corresponding to the knowledge.
If you want to print more than one line, you can use the `-p` (or `--print`) option
to print more than one line.

## Finding missing anchor points

```
Usage: knowledge anchor [OPTIONS]

  Prints warning when a knowledge is introduced but is not preceded by an
  anchor point.

Options:
  -t, --tex FILE       Your TeX file.  [required]
  -s, --space INTEGER  Number of characters tolerated between an anchor point
                       and the introduction of a knowledge. (Default value:
                       150)
  --help               Show this message and exit.
```

When one runs

    knowledge anchor -t mydocument.tex

the tool will print the lines of the document containing the
introduction of a knowledge that is not preceded by an anchor point.
The tolerance on how far away the anchor point can be from the
introduction of a knowledge can be changed with the `-s` (or `--space`)
option. The default value is 150 characters (corresponding to 2-3 lines in a
TeX document).

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
  either launch a new terminal or run `source ~/.zshrc`
  (or `source ~/.bashrc`).

- I've updated `knowledge-clustering` but I still don't have the last version:

  This can happen if you have multiple versions of `python` (and multiple versions
  of `knowledge-clustering`).
  **Solution**: Type `where python3`, and uninstall `knowledge-clustering`
  from everywhere (using `<path>/python3 -m pip uninstall knowledge-clustering`)
  except your main version of python. Try to then upgrade `knowledge-clustering`
  by running `pip3 install --upgrade knowledge-clustering`.