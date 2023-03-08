VENV-BLACK=black.venv

.PHONY: black check test coverage build deploy-test

black: 
	source ./$(VENV-BLACK)/bin/activate && black .

check: 
	mypy knowledge_clustering/*.py --check-untyped-defs # Check typing
	pylint knowledge_clustering/*.py # Linter

test:
	python -m pytest tests/ -v

coverage:
	python -m pytest tests/ --cov

build: 
	python3 -m build .

deploy-test: knowledge_clustering/_version.py
	python3 -m twine upload --repository testpypi dist/* 