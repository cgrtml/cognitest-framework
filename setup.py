"""
CogniTest Framework Setup
Author: Cagri Temel
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cognitest-framework",
    version="1.0.0",
    author="Çağrı Temel",
    author_email="CTemel@my.gcu.edu",
    description="LLM-Assisted Test Automation Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/[YOUR-USERNAME]/cognitest-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pytest>=7.4.3",
        "pytest-cov>=4.1.0",
        "requests>=2.31.0",
        "transformers>=4.36.2",
        "torch>=2.1.2",
        "accelerate>=0.25.0",
        "bitsandbytes>=0.41.3",
        "sqlalchemy>=2.0.23",
        "pydantic>=2.5.0",
    ],
)