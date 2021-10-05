SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

SOURCE_FOLDERS = src tests
MODULE_NAME = sample_package

SOURCES = $(shell find $(SOURCE_FOLDERS) -type f -name '*.py')
DOCS= $(shell find docs -type f -name '*.rst') docs/conf.py

VENV=.venv

.PHONY: install
install: $(VENV) poetry.lock

poetry.lock: pyproject.toml
	poetry install

$(VENV): poetry.lock $(SOURCES)
	if [ -d $(VENV) ]; then poetry update; fi
	poetry install
	touch $(VENV)

.PHONY: codeformat
codeformat: $(SOURCES)
	poetry run black $(SOURCE_FOLDERS)

.PHONY: test
test:
	poetry run pytest --cov-append --cov-report=html --cov=src tests

.PHONY: linter
linter: poetry.lock
	poetry run black --check $(SOURCE_FOLDERS)
	poetry run pydocstyle $(SOURCE_FOLDERS)
	poetry run flake8 $(SOURCE_FOLDERS)
	poetry run pylint --score=no --extension-pkg-whitelist=lxml src
	poetry run pylint --score=no --disable W0212 tests

.PHONY: docs
docs: $(DOCS) install
	poetry run sphinx-apidoc --force -o docs/api-docs/ src
	poetry run make html -C docs
	rm -rf docs/api-docs

.PHONY: docs-spelling
docs-spelling:
	mkdir -p docs/_static
	poetry run make spelling -C docs

.PHONY: distribution
distribution: test
	poetry build

.PHONY: clean
clean:
	rm -rf poetry.lock
	rm -rf .venv
	rm -rf .pytest-cache
	rm -rf src/$(MODULE_NAME).egg-info
	rm -rf dist/
	make clean -C docs
	rm -rf docs/api-docs/*
