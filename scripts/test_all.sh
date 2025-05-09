#!/bin/bash
# Comprehensive test script that runs all tests and generates coverage report

# Set environment variables
export PYTHONPATH=.

# First, clean up
echo "Cleaning up..."
rm -f output.pdf output.html
rm -f .coverage
rm -rf htmlcov

# Run the tests with coverage
echo "Running tests with coverage..."
python -m pytest --cov=. --cov-config=.coveragerc --cov-report=term --cov-report=html

# Open the coverage report if on Mac
if [ "$(uname)" == "Darwin" ]; then
    echo "Opening coverage report..."
    open htmlcov/index.html
fi

echo "Tests complete!"
