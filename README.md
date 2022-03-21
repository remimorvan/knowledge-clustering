# Knowledge-Clustering
Clustering notions for the [knowledge LaTeX package](https://ctan.org/pkg/knowledge).

Maintainers:
 - Rémi Morvan
 - Thomas Colcombet

## Principle

The goal of **Knowledge-Clustering** is, when using the [knowledge package](https://ctan.org/pkg/knowledge) to automatically provide suggestions to the user of what notions should be grouped together.

## Install Knowledge-Clustering

To install or upgrade **Knowledge-Clustering**, run

    python3 -m pip install --index-url https://test.pypi.org/simple/ --upgrade knowledge-clustering 

## Syntax

Write in a terminal `knowledge -h` or `knowledge-clustering -h` to display the help.
If the autocomplete for `knowledge` or `knowledge-clustering` does not work, add

    eval "`pip completion --zsh`"

to your `.zshrc` if you are using `zsh`, or add 

    eval "`pip completion --bash`"

to your `.bashrc` if you are using `bash`!