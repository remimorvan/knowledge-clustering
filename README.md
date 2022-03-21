# Knowledge-Clustering
Clustering notions for the [knowledge LaTeX package](https://ctan.org/pkg/knowledge).

## Principle

The goal of **Knowledge-Clustering** is, when using the [knowledge package](https://ctan.org/pkg/knowledge) to automatically provide suggestions to the user of what notions should be grouped together.

## Installation

To install (or upgrade) **Knowledge-Clustering**, run

    python3 -m pip install --upgrade knowledge-clustering 

and then

    knowledge-init

## Syntax

Usage:

    knowledge [-h] -n NOTION_FILE -d DIAGNOSE_FILE [-l {en}] [-s]

Optional arguments:

  | Option              | Description                       |
  | ---                 | ---                               | 
  | -h, --help          | show the help message and exit    |
  | -n NOTION_FILE, --notion NOTION_FILE | File containing the knowledges/notions defined by the user. |
  | -d DIAGNOSE_FILE, --diagnose DIAGNOSE_FILE|File containing the diagnose file produced by TeX.|
  | -l {en}, --lang {en}| Language of your TeX document.    |
  | -s, --scope         | Print the scopes defined in the notion file and print the possible meaning of those scope infered by Knowledge-Clustering. |

## FAQ 

 * When running `knowledge`, I obtain a long message error indicating "Resource punkt not found."

    **Solution**: run `knowledge-init`.

 * My shell doesn't autocomplete the command `knowledge`.

    **Solution**: depending on whether you use `zsh` or `bash` write
    
        eval "`pip completion --<shellname>`"
    (where `<shellname>` is either `zsh` or `bash`)
    in your `.zshrc` (or `.bashrc`) file and then,
    either lunch a new terminal or run `source ~/.zshrc`
    (or `source ~/.bashrc`).