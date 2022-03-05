import clingo

ctl = clingo.Control()
with open("output.lp") as f:
    problem = f.read()
    f.close()
with open("constraints.lp") as f:
    constraints = f.read()
    f.close()
ctl.add("problem", [], problem)
ctl.add("constraints", [], constraints)

ctl.ground([("problem", []), ("constraints", [])])
def on_model(x):
    # global sol
    # sol = ("%s" % x)
    print(x)
ctl.solve(on_model=on_model)
