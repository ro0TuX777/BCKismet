# ForgedFate Project Structure

This document outlines the complete project structure for the ForgedFate repository.

## 📁 Repository Structure

```
forgedfate/
├── .github/                    # GitHub-specific files
│   ├── workflows/             # CI/CD workflows
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── src/                       # Source code
│   └── forgedfate/
│       ├── __init__.py
│       ├── core/              # Core functionality
│       │   ├── __init__.py
│       │   ├── config.py      # Configuration management
│       │   ├── logger.py      # Logging system
│       │   └── exceptions.py  # Exception hierarchy
│       ├── integrations/      # External integrations
│       │   ├── __init__.py
│       │   ├── elasticsearch.py  # Elasticsearch client
│       │   ├── kismet.py      # Kismet integration
│       │   └── filebeat.py    # Filebeat management
│       ├── cli/               # Command-line tools
│       │   ├── __init__.py
│       │   ├── bulk_upload.py # Bulk upload utility
│       │   ├── test_connection.py # Connection tester
│       │   └── setup.py       # Setup utility
│       ├── utils/             # Utility functions
│       │   ├── __init__.py
│       │   ├── data_processing.py
│       │   └── validation.py
│       └── web/               # Web interface components
│           ├── __init__.py
│           └── api.py
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   │   ├── test_config.py
│   │   ├── test_elasticsearch.py
│   │   └── test_kismet.py
│   ├── integration/           # Integration tests
│   │   ├── test_end_to_end.py
│   │   └── test_elasticsearch_integration.py
│   ├── fixtures/              # Test data
│   │   ├── sample_kismet.db
│   │   └── test_config.yml
│   └── conftest.py           # Pytest configuration
├── docs/                      # Documentation
│   ├── source/               # Sphinx documentation source
│   ├── examples/             # Usage examples
│   ├── api-reference.md      # API documentation
│   ├── deployment.md         # Deployment guide
│   ├── hardware-compatibility.md
│   └── troubleshooting.md
├── scripts/                   # Utility scripts
│   ├── setup_environment.sh  # Environment setup
│   ├── install_drivers.sh    # Driver installation
│   └── backup_config.sh      # Configuration backup
├── config/                    # Configuration templates
│   ├── default.yml           # Default configuration
│   ├── production.yml        # Production template
│   └── development.yml       # Development template
├── templates/                 # File templates
│   ├── filebeat.yml          # Filebeat configuration
│   ├── elasticsearch.yml     # Elasticsearch settings
│   └── docker-compose.yml    # Docker Compose template
├── kismet/                    # Enhanced Kismet source
│   ├── http_data/            # Web interface files
│   │   ├── js/
│   │   │   └── kismet.ui.api.js
│   │   └── css/
│   │       └── kismet.ui.api.css
│   ├── connectivity_tester.cc # Connection testing
│   └── [other Kismet files]
├── .gitignore                # Git ignore rules
├── .pre-commit-config.yaml   # Pre-commit hooks
├── setup.py                  # Package setup
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Development dependencies
├── pyproject.toml           # Modern Python packaging
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker Compose configuration
├── README.md                # Main documentation
├── README_NEW.md            # Updated README (to replace)
├── CONTRIBUTING.md          # Contribution guidelines
├── CHANGELOG.md             # Version history
├── LICENSE                  # License file
├── MANIFEST.in              # Package manifest
└── ForgedFate_Kismet_Elasticsearch_Integration_Technical_Paper.md
```

## 📦 Package Structure

### Core Modules

#### `src/forgedfate/core/`
- **config.py**: Configuration management with YAML/JSON support
- **logger.py**: Structured logging with rotation and multiple outputs
- **exceptions.py**: Custom exception hierarchy for error handling

#### `src/forgedfate/integrations/`
- **elasticsearch.py**: Elasticsearch client with bulk operations
- **kismet.py**: Kismet database extraction and API integration
- **filebeat.py**: Filebeat configuration and management

#### `src/forgedfate/cli/`
- **bulk_upload.py**: Command-line bulk upload utility
- **test_connection.py**: Connection testing tool
- **setup.py**: Initial setup and configuration utility

### Test Structure

#### `tests/unit/`
- Individual component testing
- Mocked external dependencies
- Fast execution for development

#### `tests/integration/`
- Component interaction testing
- Real external services (when available)
- End-to-end workflow validation

#### `tests/fixtures/`
- Sample data files
- Test configurations
- Mock database files

### Documentation Structure

#### `docs/`
- **API Reference**: Complete REST API documentation
- **Deployment Guide**: Production deployment instructions
- **Hardware Compatibility**: Supported devices and drivers
- **Troubleshooting**: Common issues and solutions
- **Examples**: Usage examples and tutorials

## 🔧 Configuration Files

### Python Packaging
- **setup.py**: Traditional setuptools configuration
- **pyproject.toml**: Modern Python packaging (PEP 518)
- **requirements.txt**: Runtime dependencies
- **requirements-dev.txt**: Development dependencies
- **MANIFEST.in**: Package file inclusion rules

### Development Tools
- **.pre-commit-config.yaml**: Code quality hooks
- **.gitignore**: Git ignore patterns
- **pytest.ini**: Test configuration
- **mypy.ini**: Type checking configuration

### Deployment
- **Dockerfile**: Container image definition
- **docker-compose.yml**: Multi-service deployment
- **config/**: Configuration templates for different environments

## 🚀 Entry Points

### Console Scripts
```python
entry_points={
    "console_scripts": [
        "forgedfate-bulk-upload=forgedfate.cli.bulk_upload:main",
        "forgedfate-test-connection=forgedfate.cli.test_connection:main",
        "forgedfate-setup=forgedfate.cli.setup:main",
    ],
}
```

### Python API
```python
from forgedfate import Config, ElasticsearchClient, KismetDataExtractor
from forgedfate.core import get_logger
from forgedfate.integrations import ElasticsearchExporter
```

## 📋 File Purposes

### Root Level Files
- **README.md**: Main project documentation and quick start
- **CONTRIBUTING.md**: Contribution guidelines and development setup
- **CHANGELOG.md**: Version history and release notes
- **LICENSE**: Software license (GPL v2)
- **setup.py**: Package installation and distribution

### Configuration Templates
- **config/default.yml**: Default configuration values
- **config/production.yml**: Production environment template
- **config/development.yml**: Development environment template

### Scripts
- **scripts/setup_environment.sh**: Automated environment setup
- **scripts/install_drivers.sh**: Hardware driver installation
- **scripts/backup_config.sh**: Configuration backup utility

## 🔄 Development Workflow

### 1. Setup
```bash
git clone https://github.com/forgedfate/forgedfate.git
cd forgedfate
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

### 2. Development
```bash
# Make changes
# Run tests
pytest
# Check code quality
pre-commit run --all-files
# Commit changes
git commit -m "feat: add new feature"
```

### 3. Testing
```bash
# Unit tests
pytest tests/unit/
# Integration tests
pytest tests/integration/
# Coverage report
pytest --cov=src/forgedfate --cov-report=html
```

### 4. Documentation
```bash
# Build documentation
cd docs/
make html
# Serve locally
python -m http.server 8000
```

## 📦 Distribution

### PyPI Package
```bash
# Build package
python setup.py sdist bdist_wheel
# Upload to PyPI
twine upload dist/*
```

### Docker Image
```bash
# Build image
docker build -t forgedfate:latest .
# Run container
docker-compose up -d
```

## 🔒 Security Considerations

### Sensitive Files
- Configuration files with credentials
- Private keys and certificates
- Log files with sensitive data
- Database files with collected data

### .gitignore Patterns
- `*.log` - Log files
- `*.kismet` - Kismet database files
- `config.json` - Configuration with secrets
- `.env*` - Environment files
- `secrets.yml` - Secret configuration files

This structure provides a solid foundation for the ForgedFate project, ensuring maintainability, scalability, and ease of contribution.
