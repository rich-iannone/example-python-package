# ------------------------------------------------------------------------------------------------
# NOTE: This file is heavily commented because this is an educational repository. In a real
# project most of these comments would be left out; the `## ` help text on each target is
# usually all the documentation a Makefile needs.
# ------------------------------------------------------------------------------------------------

# The Makefile is the project's developer interface: short, memorable commands (`make test`,
# `make check`) for longer ones you'd otherwise have to remember or look up. Every project uses
# the same target names, so moving between repos needs no re-learning. CI runs these targets
# too, so "it passes locally" and "it passes in CI" mean the same thing.
#
# How a rule is read:
#
#   target: prerequisites  ## help text
#   <TAB>recipe line (a shell command)
#   <TAB>another recipe line
#
# - `make target` first makes each prerequisite (left to right), then runs the recipe lines.
# - Recipe lines MUST start with a tab character, not spaces. This is the classic Makefile
#   gotcha and "missing separator" errors almost always mean spaces crept in.
# - Each recipe line runs in its own shell, so `cd somewhere` doesn't carry over to the next line.
# - A leading `@` stops make from echoing the command before running it, which keeps the
#   output clean.
# - If a recipe line fails (non-zero exit), make stops there and reports an error. That's what
#   lets CI use `make test` to fail a build.
#
# What `.PHONY` means:
#
# make was designed for building files. A target name is normally a filename, and make skips the
# recipe when a file of that name already exists and is up to date. Our targets aren't files,
# they're just names for commands. Declaring them `.PHONY` tells make: "this target is not a
# file, so, always run the recipe." Without it, the moment a file or folder with the same name
# appears, the target silently stops working. Try it: remove `.PHONY: test` below, run
# `touch test`, then `make test`. Instead of running the tests, make prints
# "make: `test' is up to date." (`rm test` and restore the line afterwards.)


# Variables. `?=` sets a default that can be overridden from the command line or environment,
# e.g. `make test PYTHON=python` (which is how CI uses the runner's Python instead of .venv).
# Elsewhere, `$(PYTHON)` is replaced with the value.
PYTHON ?= .venv/bin/python

# Running `python -m pytest` (rather than plain `pytest`) guarantees the tool comes from that
# exact Python environment, without needing the venv to be activated.


# The first target in the file is the default, so plain `make` shows this help.
#
# It works by searching this Makefile ($(MAKEFILE_LIST)) for lines shaped like
# `target: ... ## help text` and printing the target name and the help text. Targets without
# `## ` (like the `clean-*` helpers at the bottom) are left out of the listing. Inside a recipe,
# `$$1` is how you write a literal `$1` (for awk), since make treats a single `$` as its own.
.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)


# ================================================================================================
# Setup
# ================================================================================================

# `-e` is an editable install: the venv points at the source folder instead of a copy, so code
# changes take effect without reinstalling. `.[dev]` means "this project, plus its `dev` extra"
# (pytest, ruff, pyright, ...; see `[project.optional-dependencies]` in pyproject.toml).
.PHONY: install
install: ## Install the package with dev extras into .venv
	@$(PYTHON) -m pip install -e ".[dev]"


# ================================================================================================
# Testing
# ================================================================================================

# The everyday command, and the one CI runs. Most pytest settings live in pyproject.toml;
# coverage options are added here so that a bare `pytest` stays quick and uncluttered while
# you're iterating, and `make test` gives the full picture.
#   --cov=tinytab               measure coverage of the package
#   --cov-report=term-missing   print the coverage table, with the line numbers never run
#   --durations 10              list the 10 slowest tests, so slow ones get noticed
.PHONY: test
test: ## Run the test suite with coverage (skips slow tests)
	@$(PYTHON) -m pytest --cov=tinytab --cov-report=term-missing --durations 10

# pyproject.toml adds `-m "not slow"` to every run. Passing `-m ""` on the command line
# replaces it with an empty filter, which selects everything.
.PHONY: test-all
test-all: ## Run all tests, including slow ones
	@$(PYTHON) -m pytest -m "" --durations 10

.PHONY: test-slow
test-slow: ## Run only the slow tests
	@$(PYTHON) -m pytest -m slow

# After an intentional change to rendered output, re-record the snapshots in
# tests/__snapshots__/ (syrupy also deletes snapshots that no test uses anymore). Always review
# the result with `git diff tests/__snapshots__` before committing.
.PHONY: test-update
test-update: ## Accept snapshot changes
	@$(PYTHON) -m pytest --snapshot-update

# A browsable report: open htmlcov/index.html to see each file with unrun lines highlighted.
.PHONY: test-cov-html
test-cov-html: ## Run tests and write an HTML coverage report to htmlcov/
	@$(PYTHON) -m pytest --cov=tinytab --cov-report=html


# ================================================================================================
# Code quality
# ================================================================================================

# Fix things: reformat the code, then apply ruff's automatic lint fixes. Use locally.
.PHONY: lint
lint: ## Run ruff formatter and linter (with fixes)
	@$(PYTHON) -m ruff format
	@$(PYTHON) -m ruff check --fix

# Check things without changing any files, and fail if something's wrong. This is the
# version for CI, where nobody is around to commit the fixes.
.PHONY: check-format
check-format: ## Check formatting and lint without making changes
	@$(PYTHON) -m ruff format --check
	@$(PYTHON) -m ruff check

# Settings (strict mode, Python version) come from `[tool.pyright]` in pyproject.toml.
.PHONY: type-check
type-check: ## Run pyright in strict mode
	@$(PYTHON) -m pyright tinytab

# A target with prerequisites and no recipe of its own: `make check` runs `lint`, then
# `type-check`, then `test`, stopping at the first failure. Run it before you push.
.PHONY: check
check: lint type-check test ## Run all checks (the pre-push gate)


# ================================================================================================
# Building
# ================================================================================================

# Creates dist/tinytab-<version>.tar.gz (the sdist: source code) and
# dist/tinytab-<version>-py3-none-any.whl (the wheel: ready to install). Old builds are removed
# first (the `clean-build` prerequisite) so that dist/ only ever holds the current version.
.PHONY: build
build: clean-build ## Build the sdist and wheel into dist/
	@$(PYTHON) -m build


# ================================================================================================
# Playground
# ================================================================================================

# Quarto runs the Python cells through a Jupyter "kernel", chosen by name (`python3`). If you
# have kernels registered elsewhere on your machine, `python3` can resolve to a different Python
# that doesn't have tinytab installed. Pointing JUPYTER_PATH at the venv makes Quarto find the
# venv's own kernel first. `$(CURDIR)` is the folder the Makefile is in.
JUPYTER_PATH := $(CURDIR)/.venv/share/jupyter

.PHONY: playground
playground: ## Render playground.qmd to HTML with Quarto
	@JUPYTER_PATH="$(JUPYTER_PATH)" QUARTO_PYTHON="$(PYTHON)" quarto render playground.qmd


# ================================================================================================
# Cleaning up
# ================================================================================================

.PHONY: clean
clean: clean-build clean-pyc clean-test ## Remove build, Python, and test artifacts

# The helper targets below have no `## ` text, so `make help` doesn't list them, but they can
# still be run directly (e.g. `make clean-test`). The `.venv` folder is skipped so the
# installed packages are left alone.

# Build output: the build/ staging folder, dist/, and setuptools' *.egg-info metadata.
.PHONY: clean-build
clean-build:
	@rm -rf build/ dist/ .eggs/
	@find . -name '*.egg-info' -not -path './.venv/*' -exec rm -rf {} +

# Python's cached bytecode.
.PHONY: clean-pyc
clean-pyc:
	@find . -name '__pycache__' -not -path './.venv/*' -exec rm -rf {} +

# pytest's cache (used by `--lf`), coverage output, and the rendered playground.
.PHONY: clean-test
clean-test:
	@rm -rf .pytest_cache .coverage htmlcov coverage.xml
	@rm -rf playground.html playground_files
