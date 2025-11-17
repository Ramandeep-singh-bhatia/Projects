"""
Setup script for Stock Analysis Agent
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
with open(requirements_file, 'r') as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="stock-analysis-agent",
    version="1.0.0",
    description="AI-powered stock market analysis agent for educational purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/stock-analysis-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "stock-agent=src.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="stock market analysis sentiment AI machine-learning finance educational",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/stock-analysis-agent/issues",
        "Source": "https://github.com/yourusername/stock-analysis-agent",
    },
)
