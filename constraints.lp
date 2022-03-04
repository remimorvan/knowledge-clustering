knowledge(X) :- known(X).
knowledge(X) :- unknown(X).

1 {belongsTo(X, B) : bag(B)} 1 :- known(X).
1 {belongsTo(X, B) : bag(B)} 1 :- unknown(X).

:- far(X, Y), belongsTo(X, B), belongsTo(Y, B).
1 {knowledge(Y) : Y != X, belongsTo(Y, B), near(X, Y)} :- belongsTo(X, B), 2 {knowledge(Y) : belongsTo(Y, B)}.

numberNonemptyBags(K) :- K = #count {bag(B) : knowledge(X), belongsTo(X, B)}.
#minimize {K@1 : numberNonemptyBags(K)}.

#show belongsTo/2.