bag(0).
known("word@ord").
belongsTo("word@ord", 0).
known("words@ord").
belongsTo("words@ord", 0).

bag(1).
known("regular language").
belongsTo("regular language", 1).
known("recognisable language").
belongsTo("recognisable language", 1).

bag(2).
known("monoid").
belongsTo("monoid", 2).
known("monoids").
belongsTo("monoids", 2).

bag(3).
known("semigroup").
belongsTo("semigroup", 3).


near("word@ord", "words@ord").
near("words@ord", "word@ord").
near("regular language", "recognisable language").
near("recognisable language", "regular language").
near("monoid", "monoids").
near("monoids", "monoid").

far("word@ord", "regular language").
far("word@ord", "recognisable language").
far("words@ord", "regular language").
far("words@ord", "recognisable language").
far("word@ord", "monoid").
far("word@ord", "monoids").
far("words@ord", "monoid").
far("words@ord", "monoids").
far("word@ord", "semigroup").
far("words@ord", "semigroup").
far("regular language", "word@ord").
far("regular language", "words@ord").
far("recognisable language", "word@ord").
far("recognisable language", "words@ord").
far("regular language", "monoid").
far("regular language", "monoids").
far("recognisable language", "monoid").
far("recognisable language", "monoids").
far("regular language", "semigroup").
far("recognisable language", "semigroup").
far("monoid", "word@ord").
far("monoid", "words@ord").
far("monoids", "word@ord").
far("monoids", "words@ord").
far("monoid", "regular language").
far("monoid", "recognisable language").
far("monoids", "regular language").
far("monoids", "recognisable language").
far("monoid", "semigroup").
far("monoids", "semigroup").
far("semigroup", "word@ord").
far("semigroup", "words@ord").
far("semigroup", "regular language").
far("semigroup", "recognisable language").
far("semigroup", "monoid").
far("semigroup", "monoids").


