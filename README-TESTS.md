# Development Guide: Surmai Itinerary Generator

This document explains the modular architecture of the Surmai Itinerary Generator and provides guidelines for future development.

## Modular Architecture

The project is organized into distinct modules with clear responsibilities:

### Core Modules

- **parser.py**: Handles loading and structuring Surmai trip data
  - `load_trip_data()`: Loads JSON data from file
  - `get_trip_timezone()`: Extracts timezone from trip destinations
  - `parse_dates()`: Converts ISO date strings to datetime objects
  - `build_days()`: Creates the base structure for each day in the itinerary

- **formatting.py**: Handles event formatting and time-related functionality
  - `insert_event()`: Adds an event to the appropriate day
  - `get_transport_icon()`: Maps transport types to emoji icons
  - `format_lodging_events()`: Formats lodging check-in/out events
  - `format_transport_events()`: Formats transportation events
  - `format_activity_events()`: Formats activity events
  - `populate_days()`: Master function that populates days with all events

- **lookups.py**: Placeholder for future data enrichment capabilities
  - Currently minimal but ready for expansion with airport codes, place data, etc.
  - Will be used to add richer metadata to locations and transportation

- **renderer.py**: Handles template rendering and PDF generation
  - `create_template_context()`: Builds the context dictionary for templates
  - `render_itinerary()`: Renders HTML using Jinja2 templates
  - `convert_to_pdf()`: Converts HTML to PDF using Gotenberg

- **generate_itinerary.py**: Main orchestrator that ties everything together
  - Provides the CLI interface
  - Coordinates the flow between parser, formatting, and renderer

### User Interface

- **app.py**: Flask web application for the UI
  - Provides file upload for trip.json and templates
  - Handles PDF generation requests

## Development Workflow

1. **Set up your development environment**:
   ```bash
   # Clone the repository
   git clone https://github.com/username/itinerary-generator.git
   cd itinerary-generator
   
   # Set up development environment
   ./setup_dev.sh
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Run tests**:
   ```bash
   # Run all tests
   ./test_all.sh
   
   # Run specific test categories
   ./run_tests.sh unit
   ./run_tests.sh integration
   ```

## Adding New Features

When adding new features, follow these guidelines:

1. **Determine the appropriate module** for your change based on responsibility
2. **Write tests first** to define the expected behavior
3. **Implement the feature** in the appropriate module
4. **Update the integration** in `generate_itinerary.py` if needed
5. **Document your changes** in the appropriate README files

### Example: Adding Airport Code Lookup

For example, to add airport code lookup:

1. Add your feature to `lookups.py`:
   ```python
   def get_airport_info(code):
       """Look up airport information by IATA code."""
       # Implementation...
   ```

2. Update `formatting.py` to use this information:
   ```python
   from lookups import get_airport_info
   
   def format_transport_events(days, transportations, tz):
       for transport in transportations:
           if transport["type"] == "flight":
               origin_info = get_airport_info(transport["origin"])
               # Use the information...
   ```

3. Write tests for your new functionality:
   ```python
   def test_get_airport_info():
       info = get_airport_info("JFK")
       assert info["name"] == "John F. Kennedy International Airport"
       assert info["city"] == "New York"
   ```

## Testing

See [README-TESTS.md](README-TESTS.md) for detailed information on testing.

## Docker

The project includes Docker configuration for containerized deployment:

```bash
# Build and run with Docker
docker-compose up --build
```

## Contribution Guidelines

1. **Use black** for code formatting
2. **Add tests** for all new functionality
3. **Document** all public functions with docstrings
4. **Maintain the modular architecture** by respecting module responsibilities
5. **Update documentation** when adding significant features

## Future Enhancements

- Richer transport details with airline/operator information
- Location enrichment with detailed address information
- Cost formatting with currency symbols
- Support for displaying attachments

## References

- [Surmai Project](https://github.com/rohitkumbhar/surmai)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Gotenberg Documentation](https://gotenberg.dev/docs/about)