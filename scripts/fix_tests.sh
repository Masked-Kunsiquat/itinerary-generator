#!/bin/bash
# Script to fix test issues

# Create directory for archiving old tests if it doesn't exist
mkdir -p tests/archive

# Move the old test directory completely
if [ -d "tests/old" ]; then
    # Create a backup
    echo "Moving old tests to archive..."
    mv tests/old/* tests/archive/
    rmdir tests/old
fi

# Fix filename with typo if it exists
if [ -f "tests/test_generate_intinerary.py" ]; then
    echo "Fixing test file name typo..."
    mv tests/test_generate_intinerary.py tests/test_generate_itinerary.py
fi

# Remove any leftover test files
echo "Cleaning up any temporary test files..."
rm -f output.pdf
rm -f output.html

# Run the unit tests
echo "Running unit tests..."
make unit-test

echo "Script complete"
