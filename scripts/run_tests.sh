#!/bin/bash
# Script to run specific tests

# Check for the command argument
if [ $# -eq 0 ]; then
    echo "Usage: ./run_tests.sh [unit|integration|all|specific]"
    echo "  unit        Run all unit tests"
    echo "  integration Run integration tests"
    echo "  all         Run all tests"
    echo "  specific    Run specific test file (e.g., ./run_tests.sh specific tests/test_parser.py)"
    exit 1
fi

# Set environment variable
export PYTHONPATH=.

case "$1" in
  unit)
    echo "Running unit tests..."
    pytest --cov=. --cov-config=.coveragerc --cov-report=term
    ;;
  integration)
    echo "Running integration tests..."
    pytest --integration --cov=. --cov-config=.coveragerc tests/test_integration.py
    ;;
  all)
    echo "Running all tests..."
    pytest --integration --cov=. --cov-config=.coveragerc
    ;;
  specific)
    if [ -z "$2" ]; then
      echo "Error: No test file specified"
      echo "Usage: ./run_tests.sh specific <test_file>"
      exit 1
    fi
    echo "Running specific test: $2"
    pytest --cov=. --cov-config=.coveragerc "$2" -v
    ;;
  *)
    echo "Unknown command: $1"
    echo "Usage: ./run_tests.sh [unit|integration|all|specific]"
    exit 1
    ;;
esac
