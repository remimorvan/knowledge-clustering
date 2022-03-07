# Knowledge-Clustering
Clustering notions for the [knowledge LaTeX package](https://ctan.org/pkg/knowledge).

Maintainers:
 - Rémi Morvan
 - Thomas Colcombet

## Principle

The goal of **Knowledge-Clustering** is, when using the [knowledge package](https://ctan.org/pkg/knowledge) to automatically provide suggestions to the user of what notions should be grouped together.

## Using Knowledge-Clustering

### Input

Knowledge-Clustering takes two input files: one file <file_notion> in which you are storing your knowledges (these
corresponds to the `tex` files in the folder `examples`), and a file <file_diagnose> produced by
the knowledge package (files with `diagnose` extension).

### Syntax

The syntax is the following: `./knowledge.py -n <file_notion> -d <file_diagnose> [options]`.
At any time, you can display the help using `./knowledge.py --help`. 


### Output

Knowledge-Clustering writes its output directly in the <file_notion> as comments. If the user accepts the suggestion,
she can simply uncomment the line. Otherwise, she must remove the line and define the notion manually.

### Examples

You can run `knowledge.py` on the examples provided.
The file `examples/small.tex` says to Knowledge-Clustering that the following notions are already defined

    \knowledge{notion}
    | word

    \knowledge{notion}
    | regular language
    | recognisable language

    \knowledge{notion}
    | monoid
    
Moreover, from the file `examples/small.diagnose` indicates that four unknown knowledges where found when compiling some
LaTeX document: "monoids", "semigroup", "words" and "semigroups".
After running `./knowledge.py -n examples/small.tex -d examples/small.diagnose`, the file `examples/small.tex` now
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
    
which means that it is suggested to the user to put "words" together with the (already known) knowledge "word@ord",
to put "monoids" with "monoid", and to define a new notion containing "semigroup" and "semigroups".

You can also run Knowledge-Clustering on an empty notion file and a (possibly) huge diagnose file.
An example is provided in `examples/big.tex` (which is empty) and `examples/big.diagnose`
(which contains 181 undefined knowledges).
