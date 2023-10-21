# Makefile for CCAI insights conversation data loading and analysis

# Define variables
VENV_DIR = ./venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
SCRIPT = run.py

.PHONY: setup run

# Default target: Run the entire flow
all: setup run

# Set up the Python virtual environment
setup:
	@echo "Setting up Python virtual environment..."
	python -m venv $(VENV_DIR)
	$(PIP) install -r requirements.txt

# Run the insights ingestion pipeline
run:
	@echo "Running insights ingestion pipeline..."
	$(PYTHON) $(SCRIPT)

# Help target to display available targets and their descriptions
help:
	@echo "Available targets:"
	@echo "  setup - Set up the Python virtual environment."
	@echo "  run   - Run the insights ingestion pipeline."
	@echo "  all   - Run both setup and run targets (default)."
	@echo "  help  - Display this help message."

# Clean up the virtual environment and any generated files (optional)
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)

# Ensure that the environment is activated before running any target
%: setup
