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

# Run prediction
predict:
	@echo "Running prediction..."
	poetry run python scripts/data-analysis-backbone-1.py/prediction.py

# Run data discovery for deaths, population and gini
discover:
	@echo "Running data discovery..."
	poetry run python scripts/data_discovery/deaths_population_gini.py

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

# Clean datasets
clean-datasets:
	@echo "Cleaning datasets..."
	rm -rf datasets/landing-zone/persistent/*
	rm -rf datasets/formatted-zone/*
	rm -rf datasets/trusted-zone/*
	rm -rf datasets/exploitation-zone/*

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
	@echo "  clean-datasets 	- Clean datasets."

# Clean up the virtual environment and any generated files (optional)
clean:
	@echo "Cleaning up venv..."
	rm -rf .venv
	@echo "Cleaning up datasets..."
	clean-datasets
