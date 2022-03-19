import config
import distance as dist
import kltex
import scope_meaning as sm

list_prefixes = config.parse("config/english.config")

with open("examples/small.tex", "r") as f:
    document, known_knowledges = kltex.parse(f)
    f.close()

list_kl = known_knowledges[2]
list_kl_broke = map(dist.breakupNotion, list_kl)
print(list_kl_broke)
print(sm.inferScope(list_kl, "ord"))
# scopes_meaning = sm.inferAllScopes(known_knowledges)
# sm.printScopes(scopes_meaning, True)
