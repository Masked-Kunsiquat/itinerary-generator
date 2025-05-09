#!/bin/bash
# Set up development environment

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing development dependencies..."
pip install -r requirements-dev.txt

# Install the package in development mode
echo "Installing package in development mode..."
pip install -e .

# Make scripts executable
echo "Making scripts executable..."
chmod +x run_tests.sh
chmod +x test_all.sh
chmod +x clean_tests.sh
chmod +x fix_tests.sh

echo "Development environment setup complete!"
echo ""
echo "Run the application with: python app.py"
echo "Run tests with: ./run_tests.sh unit"
echo "Run all tests with coverage: ./test_all.sh"
echo "Clean up test artifacts: ./clean_tests.sh"
echo ""
echo "For more information on testing, see README-TESTS.md"
