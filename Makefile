VENV-BLACK=black.venv

.PHONY: black typing lint check

black: 
	source ./$(VENV-BLACK)/bin/activate && black .

check: 
	mypy knowledge_clustering/*.py # Check typing
	pylint # Linter