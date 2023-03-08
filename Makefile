VENV-BLACK=black.venv

.PHONY: black check test coverage

black: 
	source ./$(VENV-BLACK)/bin/activate && black .

check: 
	mypy knowledge_clustering/*.py --check-untyped-defs # Check typing
	pylint knowledge_clustering/*.py # Linter

test:
	python -m pytest tests/ -v

coverage:
	python -m pytest tests/ --cov
