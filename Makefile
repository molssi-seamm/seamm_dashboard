MODULE := seamm_dashboard
.PHONY: clean clean-test clean-pyc clean-build docs help environment tags update-nodejs
.DEFAULT_GOAL := help
CONDA := $(shell command -v mamba || command -v conda)
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

ifeq ($(CONDA),)
$(error Neither mamba nor conda was found in the PATH)
endif

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

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

lint: ## check style with black and flake8
	black --check --diff devtools mac_app/*.py $(MODULE)
	flake8 devtools mac_app/*.py $(MODULE)

format: ## reformat with with yapf and isort
	black devtools mac_app/*.py $(MODULE)

typing: ## check typing
	pytype $(MODULE)

test: ## run tests quickly with the default Python
	devtools/scripts/install_chromedriver.py
	pytest -rxX

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source seamm_dashboard -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

environment: ## create the environment for running the dashboard
	@echo 'Creating the Conda/pip environment. This will take some time!'
	@echo ''
	@$(CONDA) env create --force --file devtools/conda-envs/test_env.yaml --name seamm-dashboard
	@echo ''
	@echo 'Installing the Javascript, which will also take a couple minutes!'
	@echo ''
	@echo 'Sometimes the next step will fail because it cannot find the'
	@echo 'executable "npm". If it does, just activate the new environment:'
	@echo '     $(CONDA) activate seamm-dashboard'
	@echo 'The run make again:'
	@echo '     make finish_dashboard'
	@echo ''
	@echo ''
	@cd seamm_dashboard/static && $(CONDA) run -n seamm-dashboard npm install
	@echo ''
	@echo 'To use the environment, type'
	@echo '   $(CONDA) activate seamm-dashboard'

finish_dashboard: ## finish create the environment for running the dashboard
	@echo 'Installing the Javascript, which will also take a couple minutes!'
	@echo ''
	@cd seamm_dashboard/static && npm install
	@ rm -f seamm_dashboard/static/package-lock.json
	@cd seamm_dashboard/static && python only_needed_files.py
	@echo ''
	@echo 'To use the environment, type'
	@echo '   $(CONDA) activate seamm-dashboard'

html: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/developer/$(MODULE).rst
	rm -f docs/developer/modules.rst
	sphinx-apidoc -o docs/developer $(MODULE)
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

docs: html ## Make the html docs and show in the browser
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	python -m twine upload dist/*

test-release: dist ## package and upload a release to test PyPi
	twine upload --repository testpypi dist/*

check-release: dist ## check the release for errors
	python -m twine check dist/*

dist: clean ## builds source and wheel package
	python -m build
	ls -l dist

install: uninstall nodejs ## install the package to the active Python's site-packages
	pip install .

dev-install: uninstall nodejs ## install the package to the active Python's site-packages
	pip install -e .

uninstall: clean ## uninstall the package
	pip uninstall --yes seamm-dashboard

nodejs: seamm_dashboard/static/node_modules ## install the node.js files if they are missing

seamm_dashboard/static/node_modules:
	@echo 'Installing the Javascript, which will take a couple minutes!'
	@echo ''
	@cd seamm_dashboard/static && npm install
	@ rm -f seamm_dashboard/static/package-lock.json
	@cd seamm_dashboard/static && python only_needed_files.py

update-nodejs: ## reinstall the node.js files
	@rm -fr seamm_dashboard/static/node_modules
	@echo 'Reinstalling the Javascript, which will take a couple minutes!'
	@echo ''
	@cd seamm_dashboard/static && npm install
	@ rm -f seamm_dashboard/static/package-lock.json
	@cd seamm_dashboard/static && python only_needed_files.py

tags:
	rm -f TAGS
	find $(MODULE) -type f -name '*.py' -print0 | xargs -0 etags -a	
