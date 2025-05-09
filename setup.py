from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="itinerary-generator",
    version="1.0.1",
    author="Masked-Kunsiquat",
    author_email="your.email@example.com",
    description="Generate beautiful trip itineraries from Surmai exports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Masked-Kunsiquat/itinerary-generator",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "itinerary_generator": [
            "templates/*.html",
            "static/*",
            "data/samples/*",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "jinja2",
        "requests",
        "flask",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-flask",
            "pytest-cov",
            "flake8",
            "black",
        ],
    },
    entry_points={
        "console_scripts": [
            "itinerary-cli=itinerary_generator.cli:main",
            "itinerary-web=itinerary_generator.web:app.run",
        ],
    },
)
