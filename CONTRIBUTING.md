# Contributing to Itinerary Generator

Thank you for considering contributing to the Itinerary Generator!

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/Masked-Kunsiquat/itinerary-generator.git
   cd itinerary-generator
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```
   make test
   ```

4. Start development server:
   ```
   make run-dev
   ```

## Project Structure

- `itinerary_generator/` - Main package
  - `app.py` - Flask web application
  - `generate_itinerary.py` - Main orchestration module
  - `parser.py` - Trip data parsing
  - `formatting.py` - Event formatting and timezone handling
  - `lookups.py` - Data enrichment (placeholders for now)
  - `renderer.py` - Template rendering and PDF conversion
  - `data/` - Sample data files
  - `templates/` - Jinja2 templates
  - `static/` - Static files (CSS, JS, etc.)

- `tests/` - Test suite
  - Unit tests for each module
  - Integration tests

## Adding Features

Please refer to the goals.md file for planned features and enhancements.
