.PHONY: install lint test clean docs run

install:
	poetry install

lint:
	poetry run black .
	poetry run isort .
	poetry run flake8 .

test:
	poetry run pytest

coverage:
	poetry run pytest --cov=src tests/ --cov-report=term-missing

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "*.pyc" -exec rm -rf {} +
	find . -type d -name "*.pyo" -exec rm -rf {} +
	find . -type d -name "*.pyd" -exec rm -rf {} +
	find . -type d -name ".DS_Store" -exec rm -rf {} +

docs:
	cd docs && poetry run mkdocs serve

run:
	poetry run streamlit run main.py

setup: install
	pre-commit install
	cp .env.example .env

update:
	poetry update

help:
	@echo "make install    - Install dependencies"
	@echo "make lint       - Run linting tools"
	@echo "make test       - Run tests"
	@echo "make coverage   - Run tests with coverage report"
	@echo "make clean      - Clean up cache files"
	@echo "make docs       - Serve documentation locally"
	@echo "make run        - Run the application"
	@echo "make setup      - Initial setup (install deps, setup pre-commit, copy env)"
	@echo "make update     - Update dependencies" 