# Project Changes and Notes

## Environment
- Windows 11 x64
- Python 3.13
- Poetry for dependency management
- Pydantic v2.9.0+
- MongoDB for database

## Recent Changes

### 2025-02-22
- Added GitHub Actions workflow for automated linting (black, isort, flake8)
- Added flake8 configuration file
- Fixed issue with resume preamble loading in LaTeX compilation
- Consolidated user preference models into a single file
- Updated model configurations for better type safety

## Important Notes
- The project uses Poetry for dependency management
- All models are using Pydantic v2 with proper type hints
- MongoDB is used as the primary database
- LaTeX is used for document generation
- Automated linting is configured via GitHub Actions

## Warnings
- Always ensure proper type hints are used with Pydantic v2
- Check MongoDB connection before operations
- Handle LaTeX compilation errors gracefully
- Keep track of model versioning for LLMs
- Run linting locally before pushing changes

## Future Considerations
- Consider adding more test coverage
- Monitor LaTeX compilation performance
- Keep dependencies up to date
- Consider adding more documentation
- Consider adding pre-commit hooks for linting

## Dependencies
Key dependencies and their versions:
- pydantic >= 2.9.0
- anthropic >= 0.40.0, < 0.41.0
- openai >= 1.57.2, < 1.58.0
- fastapi >= 0.104.0, < 0.105.0
- streamlit >= 1.41.0, < 1.42.0
- pymongo >= 4.10.1, < 4.11.0

## Development Tools
- black (code formatting)
- isort (import sorting)
- flake8 (code linting)
- GitHub Actions (CI/CD) 