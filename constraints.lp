knowledge(X) :- known(X).
knowledge(X) :- unknown(X).

1 {belongsTo(X, B) : bag(B)} 1 :- known(X).
1 {belongsTo(X, B) : bag(B)} 1 :- unknown(X).

:- far(X, Y), belongsTo(X, B), belongsTo(Y, B).
1 {belongsTo(Y, B) : Y != X, knowledge(Y), near(X, Y)} :- belongsTo(X, B), 2 {knowledge(Y) : belongsTo(Y, B)}.

numberNonemptyBags(K) :- K = #count {bag(B) : knowledge(X), belongsTo(X, B)}.
#minimize {K@1 : numberNonemptyBags(K)}.

belongsToUnkown(X, B) :- belongsTo(X,B), unknown(X).

#show belongsToUnkown/2.
#defined known/1.
#defined unknown/1.
#defined knwoledge/1.
#defined belongsTo/2.
#defined belongsToUnkown/2.
#defined bag/1.
#defined numberNonemptyBags/1.