# Contributing to Resume Builder TeX

Thank you for your interest in contributing to Resume Builder TeX! This document provides guidelines and instructions for contributing.

## Development Environment

1. **Prerequisites**
   - Python 3.13
   - Poetry for dependency management
   - MongoDB
   - LaTeX installation

2. **Setup**
   ```bash
   # Clone the repository
   git clone https://github.com/mucahitkayadan/Resume-Builder-TeX.git
   cd Resume-Builder-TeX

   # Install dependencies
   poetry install
   ```

## Code Style

- Follow PEP 8 guidelines
- Use Black formatter with line length 88
- Use isort for import sorting
- Use proper type hints with Pydantic v2
- Document all functions and classes with docstrings

## Testing

- Write unit tests for all new features
- Write integration tests for all new features
- Maintain test coverage above 80%
- Run tests before submitting PR:
  ```bash
  poetry run pytest
  ```

## Pull Request Process

1. Create a feature branch (`feature/your-feature-name`)
2. Make your changes
3. Run linting and tests
4. Update documentation
5. Submit PR with clear description

## Documentation

- Update docstrings for any new code
- Update README.md if needed
- Update CHANGELOG.md
- Keep technical documentation up to date

## Commit Messages

Follow conventional commits format:
```
feat: add new feature
fix: resolve bug
docs: update documentation
test: add tests
refactor: improve code structure
```

## Questions?

Feel free to open an issue for any questions or concerns. 