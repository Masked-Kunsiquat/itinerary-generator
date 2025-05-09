"""
Test configuration for pytest.
"""
import sys
import os
import pytest
import json
import tempfile

# Path to the sample data
SAMPLE_DATA_PATH = os.path.join("itinerary_generator", "data", "samples", "trip.sample.json")


@pytest.fixture
def sample_trip_data():
    """Sample trip data for testing."""
    with open(SAMPLE_DATA_PATH, "r") as f:
        return json.load(f)


@pytest.fixture
def fake_json_file():
    """Create a temporary JSON file for testing."""
    content = {
        "trip": {
            "name": "Test Trip",
            "startDate": "2025-05-10T00:00:00Z",
            "endDate": "2025-05-12T00:00:00Z",
            "destinations": [{"timezone": "UTC"}]
        },
        "activities": [],
        "lodgings": [],
        "transportations": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(content, tmp)
        temp_path = tmp.name
    
    yield temp_path
    
    # Clean up
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def fake_template_file():
    """Create a temporary template file for testing."""
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ trip_name }}</title>
    </head>
    <body>
        <h1>{{ trip_name }}</h1>
        <p>{{ start_date }} - {{ end_date }}</p>
        {% for day in days %}
        <div>
            <h2>{{ day.date }}</h2>
            <ul>
                {% for time, label in day.events %}
                <li>{{ label }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </body>
    </html>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
        tmp.write(content)
        temp_path = tmp.name
    
    yield temp_path
    
    # Clean up
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def skip_integration(request):
    """Skip integration tests unless explicitly requested."""
    if request.node.get_closest_marker('integration') and not request.config.getoption('--integration'):
        pytest.skip('Integration test skipped. Use --integration to run.')


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    parser.addoption(
        '--integration',
        action='store_true',
        default=False,
        help='Run integration tests'
    )