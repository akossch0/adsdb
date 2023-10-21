SCRIPT = run.py

.PHONY: run format lint help clean

# Default target: Run the entire flow
all: run

# Install dependencies
install:
	@echo "Installing dependencies..."
	poetry install

# Run the insights ingestion pipeline
run:
	@echo "Running insights ingestion pipeline..."
	poetry run python $(SCRIPT)

# Code formatting using black
format:
	@echo "Running code formatting..."
	poetry run black scripts/
	poetry run black $(SCRIPT)

# Run Flake8 for code linting
lint:
	@echo "Running Flake8 for code linting..."
	poetry run flake8

# Help target to display available targets and their descriptions
help:
	@echo "Available targets:"
	@echo "  run           - Run the insights ingestion pipeline."
	@echo "  format        - Run code formatting using black."
	@echo "  lint          - Run Flake8 for code linting."
	@echo "  help          - Display this help message."
	@echo "  clean         - Clean up virtual environment and generated files."

# Clean up the virtual environment and any generated files (optional)
clean:
	@echo "Cleaning up..."
	poetry env remove $(shell poetry env info -p)
