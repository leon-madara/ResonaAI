#!/usr/bin/env python3
"""
Setup script for ResonaAI Demo Data Generator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#') and not line.startswith('-')
        ]

setup(
    name="resona-demo-data-generator",
    version="1.0.0",
    author="ResonaAI Team",
    author_email="dev@resonaai.com",
    description="Demo Data Generator for ResonaAI Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/resonaai/demo-data-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
            "pytest-cov>=4.1.0",
        ],
        "testing": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "resona-demo=demo_data_generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "demo_data_generator": [
            "cultural_knowledge.py",
            "*.md",
            "tests/*.py",
        ],
    },
    zip_safe=False,
    keywords="demo data generator testing ai mental-health",
    project_urls={
        "Bug Reports": "https://github.com/resonaai/demo-data-generator/issues",
        "Source": "https://github.com/resonaai/demo-data-generator",
        "Documentation": "https://github.com/resonaai/demo-data-generator/blob/main/README.md",
    },
)