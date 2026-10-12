PYTHON ?= .venv/bin/python

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install the package with dev extras into .venv
	@$(PYTHON) -m pip install -e ".[dev]"

.PHONY: test
test: ## Run the test suite with coverage (skips slow tests)
	@$(PYTHON) -m pytest --cov=tinytab --cov-report=term-missing --durations 10

.PHONY: test-all
test-all: ## Run all tests, including slow ones
	@$(PYTHON) -m pytest -m "" --durations 10

.PHONY: test-slow
test-slow: ## Run only the slow tests
	@$(PYTHON) -m pytest -m slow

.PHONY: test-update
test-update: ## Accept snapshot changes
	@$(PYTHON) -m pytest --snapshot-update

.PHONY: test-cov-html
test-cov-html: ## Run tests and write an HTML coverage report to htmlcov/
	@$(PYTHON) -m pytest --cov=tinytab --cov-report=html

.PHONY: lint
lint: ## Run ruff formatter and linter (with fixes)
	@$(PYTHON) -m ruff format
	@$(PYTHON) -m ruff check --fix

.PHONY: check-format
check-format: ## Check formatting and lint without making changes
	@$(PYTHON) -m ruff format --check
	@$(PYTHON) -m ruff check

.PHONY: type-check
type-check: ## Run pyright in strict mode
	@$(PYTHON) -m pyright tinytab

.PHONY: check
check: lint type-check test ## Run all checks (the pre-push gate)

.PHONY: build
build: clean-build ## Build the sdist and wheel into dist/
	@$(PYTHON) -m build

.PHONY: clean
clean: clean-build clean-pyc clean-test ## Remove build, Python, and test artifacts

.PHONY: clean-build
clean-build:
	@rm -rf build/ dist/ .eggs/
	@find . -name '*.egg-info' -not -path './.venv/*' -exec rm -rf {} +

.PHONY: clean-pyc
clean-pyc:
	@find . -name '__pycache__' -not -path './.venv/*' -exec rm -rf {} +

.PHONY: clean-test
clean-test:
	@rm -rf .pytest_cache .coverage htmlcov coverage.xml
