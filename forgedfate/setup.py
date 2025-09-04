#!/usr/bin/env python3
"""
ForgedFate: Kismet-Elasticsearch Integration Platform
Setup script for installation and distribution
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="forgedfate",
    version="1.0.0",
    author="ForgedFate Development Team",
    author_email="dev@forgedfate.com",
    description="Comprehensive wireless intelligence platform integrating Kismet with Elasticsearch",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/forgedfate/forgedfate",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "pre-commit>=2.15.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "forgedfate-bulk-upload=forgedfate.cli.bulk_upload:main",
            "forgedfate-test-connection=forgedfate.cli.test_connection:main",
            "forgedfate-setup=forgedfate.cli.setup:main",
        ],
    },
    include_package_data=True,
    package_data={
        "forgedfate": [
            "config/*.yml",
            "config/*.json",
            "templates/*.yml",
            "templates/*.json",
        ],
    },
    zip_safe=False,
    keywords="kismet elasticsearch wireless monitoring security intelligence",
    project_urls={
        "Bug Reports": "https://github.com/forgedfate/forgedfate/issues",
        "Source": "https://github.com/forgedfate/forgedfate",
        "Documentation": "https://forgedfate.readthedocs.io/",
    },
)
