PYTHON ?= python3
PIP ?= pip
MAYBE_UV = uv
PIP_COMPILE = uv pip compile

PACKAGES_PATH=$(PWD)/packages
PY_VENV=$(PWD)/venv
PY_VENV_REL_PATH=$(subst $(PWD)/,,$(PY_VENV))

PY_PATH=$(PWD)/src
RUN_PY = PYTHONPATH=$(PY_PATH) $(PYTHON) -m

PY_FIND_COMMAND = find . -name '*.py' | grep -vE "($(PY_VENV_REL_PATH))"
PY_FILES = $(shell $(PY_FIND_COMMAND))
BLACK_CMD = for f in $(PY_FILES); do $(RUN_PY) black --line-length 100 "$$f"; done
BLACK_CHECK_CMD = for f in $(PY_FILES); do $(RUN_PY) black --line-length 100 --check --diff "$$f"; done
MYPY_CONFIG=$(PWD)/mypy_config.ini

init:
	@if [ -d "$(PY_VENV_REL_PATH)" ]; then \
		echo "\033[33mVirtual environment already exists\033[0m"; \
	else \
		$(PYTHON) -m venv $(PY_VENV_REL_PATH); \
	fi
	@echo "\033[0;32mRun 'source $(PY_VENV_REL_PATH)/bin/activate' to activate the virtual environment\033[0m"

install:
	$(PIP) install --upgrade pip
	$(PIP) install uv
	$(PIP_COMPILE) --strip-extras --output-file=$(PACKAGES_PATH)/requirements.txt $(PACKAGES_PATH)/base_requirements.in
	$(MAYBE_UV) pip install -r $(PACKAGES_PATH)/requirements.txt

install_dev:
	$(PIP) install --upgrade pip
	$(PIP) install uv
	$(PIP_COMPILE) --strip-extras --output-file=$(PACKAGES_PATH)/requirements-dev.txt $(PACKAGES_PATH)/base_requirements.in $(PACKAGES_PATH)/dev_requirements.in
	$(MAYBE_UV) pip install -r $(PACKAGES_PATH)/requirements-dev.txt

format: isort
	$(BLACK_CMD)

check_format:
	$(BLACK_CHECK_CMD)

mypy:
	$(RUN_PY) mypy $(shell $(PY_FIND_COMMAND)) --config-file $(MYPY_CONFIG) --no-namespace-packages

pylint:
	PYLINTHOME=.pylint.d $(RUN_PY) pylint $(shell $(PY_FIND_COMMAND))

isort:
	isort $(shell $(PY_FIND_COMMAND))

lint: check_format mypy pylint

lint_full: lint

test:
	$(RUN_PY) unittest discover -s test -p *_test.py -v

clean:
	rm -rf $(PY_VENV)
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf packages/requirements*.txt

.PHONY: init install install_dev format check_format mypy pylint isort lint lint_full test clean
