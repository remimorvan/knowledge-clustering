# Anakin
Clustering notions of the [knowledge LaTeX package](https://ctan.org/pkg/knowledge). **Anakin** stands for "Automated Notion Agregation for Knowledge: It's Np-hard". It is written in Python and uses [Answer Set Programming](https://potassco.org/).

Maintainers:
 - Rémi Morvan
 - Thomas Colcombet

## Principle

The goal of **Anakin** is, when using the [knowledge package](https://ctan.org/pkg/knowledge) to automatically provide suggestions to the user of what notions should be grouped together.

## Dependencies

Anakin requires **python3** and the Python library **clingo**.
Assuming that you have **python3** and **pip** installed, you can install **clingo** by running
the following command line:

    python3 -m pip install clingo

## Using Anakin

### Input

Anakin takes two input files: one file <file_notion> in which you are storing your knowledges (these
corresponds to the `tex` files in the folder `examples`), and a file <file_diagnose> produced by
the knowledge package (files with `diagnose` extension).

### Syntax

The syntax is the following: `./anakin.py -n <file_notion> -d <file_diagnose> [options]`. You can write
`--notion` and `--diagnose` instead of `-n` and `-d`, respectively.
At any time, you can display the help using `./anakin.py --help`. 
At this time, the only possible option is `-o` (or `--optimal`) which forces the program to return the best
solution. You **should** use this option if you have few knowledges, but **should not** use it if you
have big files.

### Output

Anakin writes its output directly in the <file_notion> as comments. If the user accepts the suggestion,
she can simply uncomment the line. Otherwise, she must remove the line and define the notion manually.

### Examples

You can run anakin on the examples provided. The file `examples/small.tex` says to Anakin that the
following notions are already defined

    \knowledge{notion}
    | word

    \knowledge{notion}
    | regular language
    | recognisable language

    \knowledge{notion}
    | monoid
    
Moreover, from the file `examples/small.diagnose` indicates that three unknown knowledges where found when compiling some
LaTeX document: "monoids", "semigroup", "words" and "semigroups".
After running `./anakin.py -n examples/small.tex -d examples/small.diagnose`, the file `examples/small.tex` now
contains:

    \knowledge{notion}
    | word
    %  | words

    \knowledge{notion}
    | regular language
    | recognisable language

    \knowledge{notion}
    | monoid
    %  | monoids
    %%%%% NEW KNOWLEDGES 
    %
    %\knowledge{notion}
    %  | semigroups
    %  | semigroup
    
which means that Anakin suggest to put "words" together with the (already known) knwoledge "word@ord",
to put "monoids" with "monoid", and to define a new notion containing "semigroup" and "semigroups".