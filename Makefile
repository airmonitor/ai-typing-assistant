# Set the desired Python interpreter (change if needed)
PYTHON := python3.11
VENV := .venv
STAGE?=ppe

.PHONY: all venv activate test clean pre-commit update help

all: venv activate install # Initialize complete development environment

venv: # Create new Python virtual environment
	uv venv --seed --python $(PYTHON) $(VENV)

activate: # Activate Python virtual environment
	@. $(VENV)/bin/activate

install: # Install all project dependencies and development tools
	pip install --upgrade pip
	pip install uv
	uv pip install --upgrade pip
	uv pip install -r requirements.txt
	uv pip install pre-commit pytest pytest-snapshot

pre-commit: # Run code quality checks on all Python files
	pre-commit install
	pre-commit run --files *.py

update: # Update all dependencies and tools to latest versions
	pur -r requirements.txt
	pre-commit autoupdate

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)



.PHONY: all venv activate clean pre-commit update
