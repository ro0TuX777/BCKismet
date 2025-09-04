# Contributing to ForgedFate

Thank you for your interest in contributing to ForgedFate! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Operating system and version
   - Python version
   - ForgedFate version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs

### Suggesting Features

1. **Check the roadmap** to see if it's already planned
2. **Open a feature request** with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach
   - Any relevant examples or references

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Make your changes** following our guidelines
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Instructions

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/forgedfate.git
cd forgedfate

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest tests/
```

## 📝 Coding Standards

### Python Style Guide

- Follow **PEP 8** style guidelines
- Use **type hints** for function parameters and return values
- Write **docstrings** for all public functions and classes
- Keep line length to **88 characters** (Black formatter default)

### Code Quality Tools

We use several tools to maintain code quality:

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/

# Run all checks
pre-commit run --all-files
```

### Documentation Standards

- Use **Google-style docstrings**
- Include **type information** in docstrings
- Provide **examples** for complex functions
- Update **README.md** for user-facing changes

Example docstring:
```python
def extract_devices(self, db_path: str) -> List[Dict[str, Any]]:
    """
    Extract device information from Kismet database.
    
    Args:
        db_path: Path to the Kismet SQLite database file
        
    Returns:
        List of device dictionaries with normalized fields
        
    Raises:
        FileSystemError: If database file cannot be accessed
        DataProcessingError: If database format is invalid
        
    Example:
        >>> extractor = KismetDataExtractor("sensor-01")
        >>> devices = extractor.extract_devices("/path/to/kismet.kismet")
        >>> print(f"Found {len(devices)} devices")
    """
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interaction
├── fixtures/       # Test data and fixtures
└── conftest.py     # Pytest configuration and shared fixtures
```

### Writing Tests

- Write tests for **all new functionality**
- Use **descriptive test names** that explain what is being tested
- Follow **AAA pattern** (Arrange, Act, Assert)
- Use **fixtures** for common test data
- Mock **external dependencies** (Elasticsearch, file system, etc.)

Example test:
```python
def test_extract_devices_returns_normalized_data(mock_kismet_db):
    """Test that device extraction returns properly normalized data."""
    # Arrange
    extractor = KismetDataExtractor("test-device")
    
    # Act
    devices = extractor.extract_devices(mock_kismet_db)
    
    # Assert
    assert len(devices) > 0
    assert all("device_name" in device for device in devices)
    assert all("@timestamp" in device for device in devices)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/forgedfate --cov-report=html

# Run specific test file
pytest tests/unit/test_elasticsearch.py

# Run tests matching pattern
pytest -k "test_extract"

# Run tests with verbose output
pytest -v
```

## 📋 Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
2. **Run code quality checks**
3. **Update documentation**
4. **Add changelog entry** if applicable
5. **Rebase on latest main** branch

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by maintainers
3. **Testing** in development environment
4. **Approval** and merge by maintainers

## 🏷️ Release Process

### Version Numbering

We follow **Semantic Versioning** (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Create release notes
4. Tag release in Git
5. Build and publish packages
6. Update documentation

## 🌟 Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md** file
- **Release notes**
- **GitHub contributors** page
- **Annual contributor highlights**

## 📞 Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Email**: dev@forgedfate.com for private inquiries
- **Documentation**: Check existing docs before asking

## 📄 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 📚 Additional Resources

- **[Technical Paper](ForgedFate_Kismet_Elasticsearch_Integration_Technical_Paper.md)**: System architecture and design
- **[API Documentation](docs/api-reference.md)**: REST API reference
- **[Deployment Guide](docs/deployment.md)**: Production deployment
- **[Troubleshooting Guide](docs/troubleshooting.md)**: Common issues and solutions

Thank you for contributing to ForgedFate! 🚀
