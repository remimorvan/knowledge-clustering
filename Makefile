VENV-BLACK=black.venv

.PHONY: black check test

black: 
	source ./$(VENV-BLACK)/bin/activate && black .

check: 
	mypy knowledge_clustering/*.py --check-untyped-defs # Check typing
	pylint knowledge_clustering/*.py # Linter

test:
	python -m pytest tests/test_clustering.py -v
	python -m pytest tests/test_addquotes.py -v
	python -m pytest tests/test_anchor.py -v