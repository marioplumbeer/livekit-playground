.PHONY: init_install_os_deps init_setup_python init_setup_poetry init install

PYTHON_VERSION := $(shell cat .python-version)
PIP_VERSION := 26.0.1

init_install_os_deps:
	brew install direnv
	brew install poetry
	brew install pyenv
	brew install livekit-cli

init_setup_python:
	[[ "$$(pyenv local)" == "$(PYTHON_VERSION)" ]] || pyenv install $(PYTHON_VERSION)
	pyenv local $(PYTHON_VERSION)
	pip install --upgrade pip==$(PIP_VERSION)

init_setup_poetry:
	poetry env activate
	poetry config virtualenvs.in-project true
	poetry install --with dev
	poetry run pre-commit install

init: init_install_os_deps init_setup_python init_setup_poetry

install:
	poetry install --with dev

test:
	poetry run pytest

lint:
	poetry run ruff check --fix .

format:
	poetry run ruff format .

auth:
	lk cloud auth
