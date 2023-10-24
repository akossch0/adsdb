.PHONY: run format lint help clean

# Default target: Run the entire flow
all: run

# Install dependencies
install:
	@echo "Installing dependencies..."
	poetry install

# Code formatting using black
format:
	@echo "Running code formatting..."
	poetry run black scripts/

# Run Flake8 for code linting
lint:
	@echo "Running Flake8 for code linting..."
	poetry run flake8

# Run landing-zone
run-landing:
	@echo "Running landing-zone..."
	poetry run python scripts/landing-zone/landing-zone.py

# Run formatted-zone
run-formatted:
	@echo "Running formatted-zone..."
	poetry run python scripts/formatted-zone/formatted-zone.py

# Run trusted-zone
run-trusted:
	@echo "Running trusted-zone..."
	poetry run python scripts/trusted-zone/trusted-zone.py

# Run exploitation-zone
run-exploitation:
	@echo "Running exploitation-zone..."
	poetry run python scripts/exploitation-zone/exploitation-zone.py

# Run all zones
run: run-landing run-formatted run-trusted run-exploitation

# Help target to display available targets and their descriptions
help:
	@echo "Available targets:"
	@echo "  format        		- Run code formatting using black."
	@echo "  lint          		- Run Flake8 for code linting."
	@echo "  help          		- Display this help message."
	@echo "  clean         		- Clean up virtual environment and generated files."
	@echo "  run-landing   		- Run landing-zone."
	@echo "  run-formatted 		- Run formatted-zone."
	@echo "  run-trusted   		- Run trusted-zone."
	@echo "  run-exploitation 	- Run exploitation-zone."
	@echo "  run           		- Run all zones."

# Clean up the virtual environment and any generated files (optional)
clean:
	@echo "Cleaning up..."
	poetry env remove $(shell poetry env info -p)
