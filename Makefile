.PHONY: clean clean-test clean-pyc clean-build docs help environment
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	find . -name '.pytype' -exec rm -fr {} +

lint: ## check style with yapf
	yapf --diff --recursive  app
	flake8  app

flake: ## check the style with flake8
	flake8  app

format: ## reformat with with yapf and isort
	yapf --recursive --in-place  app

typing: ## check typing
	pytype app_ff_util

test: ## run tests quickly with the default Python
	devtools/scripts/install_chromedriver.py
	pytest

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source app -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

environment: ## create the environment for running the dashboard
	@echo 'Creating the Conda/pip environment. This will take some time!'
	@echo ''
	@conda env create --force --file seamm-dashboard.yml
	@echo ''
	@echo 'Installing the Javascript, which will also take a couple minutes!'
	@echo ''
	@echo 'Sometimes the next step will fail because it cannot find the'
	@echo 'executable "npm". If it does, just activate the new environment:'
	@echo '     conda activate seamm-dashboard'
	@echo 'The run make again:'
	@echo '     make finish_dashboard'
	@echo ''
	@echo ''
	@cd app/static && npm install
	@echo ''
	@echo 'To use the environment, type'
	@echo '   conda activate seamm-dashboard'

finish_dashboard: ## finish create the environment for running the dashboard
	@echo 'Installing the Javascript, which will also take a couple minutes!'
	@echo ''
	@cd app/static && npm install
	@echo ''
	@echo 'To use the environment, type'
	@echo '   conda activate seamm-dashboard'

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/app.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ app
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: clean ## package and upload a release
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: uninstall ## install the package to the active Python's site-packages
	python setup.py install

uninstall: clean ## uninstall the package
	pip uninstall --yes seamm-dashboard
