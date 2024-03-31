# Makefile for setting up and activating a Python virtual environment

# Set the desired Python interpreter (change if needed)
PYTHON := python3.11

# Virtual environment directory
VENV := .venv

STAGE?=ppe

# Default target
all: venv activate install

# Create the virtual environment
venv:
	@echo "Creating Python virtual environment..."
	$(PYTHON) -m venv $(VENV)

# Activate the virtual environment
activate:
	@echo "Activating Python virtual environment..."
	@echo "Run 'deactivate' to exit the virtual environment."
	@. $(VENV)/bin/activate

install:
	@echo "Installing dependencies from requirements files"
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install pre-commit pytest pytest-snapshot


pre-commit:
	@echo "Running pre-commit"
	pre-commit install
	pre-commit run --files *.py

update:
	@echo "Updating used tools and scripts"
	pre-commit autoupdate

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)



.PHONY: all venv activate clean pre-commit update
