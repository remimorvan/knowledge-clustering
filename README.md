# Knowledge-Clustering
Clustering notions for the [knowledge LaTeX package](https://ctan.org/pkg/knowledge).

## Principle

The goal of **Knowledge-Clustering** is, when using the [knowledge package](https://ctan.org/pkg/knowledge) to automatically provide suggestions to the user of what notions should be grouped together.

## Install Knowledge-Clustering

To install or upgrade **Knowledge-Clustering**, run

    python3 -m pip install --index-url https://test.pypi.org/simple/ --upgrade knowledge-clustering 

## Syntax

Write in a terminal `knowledge -h` to display the help.

### Enabling autocomplete

If the autocomplete for `knowledge` does not work, add

    eval "`pip completion --<foo>`"

to your `.<foo>rc`, where `<foo>` is either `zsh` or `bash` (or possibly another shell),
and them run 

    source ~/.<foo>rc

in your terminal.