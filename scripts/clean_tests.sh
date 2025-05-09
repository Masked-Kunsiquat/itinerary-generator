#!/bin/bash
# Script to clean up test files and run tests

echo "Cleaning up test files..."

# Remove archive directory with old tests
if [ -d "tests/archive" ]; then
    echo "Removing tests/archive directory..."
    rm -rf tests/archive
fi

# Remove __pycache__ directories
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove other test artifacts
echo "Removing temporary test files..."
rm -f output.pdf
rm -f output.html
rm -f .coverage
rm -rf htmlcov

echo "Running all tests..."
python -m pytest

echo "Clean up complete!"
