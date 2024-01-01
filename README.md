# Project Setup and Prerequisites for ADSDB - Data Management Backbone - Operations

## Project Overview

This project is designed to run an data pipeline using a GitHub Workflow. It includes targets for installing dependencies, code formatting, code linting, and cleaning up the virtual environment.

## Prerequisites

Before you begin, ensure that you have the following prerequisites installed on your system:

- **Make**: Make sure you have `Make` installed on your system.

- **Python version 3.10.12**: Make sure you have Python installed on your system. I recommend using `pyenv`.

- **Poetry**: This project uses Poetry for dependency management. Try running 
    ```bash
    pip install poetry
    ```

## Project Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/akossch0/adsdb.git
   cd adsdb
   ```

2. **Install Dependencies:**
   ```bash
   make install
   ```

   This command will use Poetry to install the project dependencies.

## Available Targets

- **Install Dependencies:**
  ```bash
  make install
  ```
  This target installs project dependencies using Poetry.

- **Format Code:**
  ```bash
  make format
  ```
  This target uses Black to format the code in the `scripts/` directory.

- **Lint Code:**
  ```bash
  make lint
  ```
  This target runs Flake8 for code linting to ensure code quality.
- **Predict on test set**
  ```bash
  make predict
  ```
  This target executes model prediction operating on data from `datasets/predict/input`.
- **Run Landing Zone:**
  ```bash
  make run-landing
  ```
  This target executes the landing-zone script.

- **Run Formatted Zone:**
  ```bash
  make run-formatted
  ```
  This target executes the formatted-zone script.

- **Run Trusted Zone:**
  ```bash
  make run-trusted
  ```
  This target executes the trusted-zone script.

- **Run Exploitation Zone:**
  ```bash
  make run-exploitation
  ```
  This target executes the exploitation-zone script.

- **Run All Zones:**
  ```bash
  make run
  ```
  This target runs all zones: landing, formatted, trusted, and exploitation.

- **Clean Datasets:**
  ```bash
  make clean-datasets
  ```
  This target cleans up datasets in landing, formatted, trusted, and exploitation zones.

- **Display Help:**
  ```bash
  make help
  ```
  This target displays information about the available targets and their descriptions.

- **Clean Up:**
  ```bash
  make clean
  ```
  This target cleans up the virtual environment and any generated files. Use this when you want to reset the project.

## Additional Notes

- **Virtual Environment:**
  The project uses Poetry to manage a virtual environment. The virtual environment is created and managed by Poetry to isolate project dependencies.

- **Code Formatting:**
  The project uses Black for code formatting. You can run `make format` to automatically format the code according to the Black style.

- **Code Linting:**
  Flake8 is used for code linting to ensure adherence to coding standards and identify potential issues in the code.

- **Cleaning Up:**
  If needed, you can run `make clean` to remove the virtual environment and any generated files, providing a clean slate for the project.
