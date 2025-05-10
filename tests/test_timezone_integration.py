"""
Test module for end-to-end timezone handling integration
"""
import pytest
import os
import tempfile
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch, MagicMock

from itinerary_generator.generate_itinerary import generate_itinerary, adjust_incorrect_utc_timestamps
from itinerary_generator.parser import load_trip_data, parse_dates
from itinerary_generator.formatting import insert_event, format_transport_events
from itinerary_generator.renderer import create_template_context


@pytest.fixture
def sample_trip_json():
    """Create a temporary trip.json file with test data."""
    trip_data = {
        "trip": {
            "name": "Test Trip",
            "startDate": "2025-05-10T09:00:00Z",  # This Z suffix should be stripped
            "endDate": "2025-05-15T17:00:00Z",    # This Z suffix should be stripped
            "destinations": [
                {"name": "New York", "timezone": "America/New_York"}
            ]
        },
        "lodgings": [
            {
                "name": "Test Hotel",
                "startDate": "2025-05-10T14:00:00Z",  # This Z suffix should be stripped
                "endDate": "2025-05-15T10:00:00Z"     # This Z suffix should be stripped
            }
        ],
        "transportations": [
            {
                "type": "flight",
                "origin": "JFK",
                "destination": "LAX",
                "departure": "2025-05-10T08:00:00Z",  # This Z suffix should be stripped
                "arrival": "2025-05-10T11:00:00Z"     # This Z suffix should be stripped
            }
        ],
        "activities": [
            {
                "name": "Museum Visit",
                "startDate": "2025-05-11T10:00:00Z"  # This Z suffix should be stripped
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(trip_data, f)
        json_path = f.name
    
    yield json_path
    
    # Clean up
    if os.path.exists(json_path):
        os.unlink(json_path)


@pytest.fixture
def template_html():
    """Create a simple template HTML file."""
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ trip_name }}</title>
    </head>
    <body>
        <h1>{{ trip_name }}</h1>
        <p>{{ start_date }} - {{ end_date }}</p>
        <p>Timezone: {{ timezone }}</p>
        {% for day in days %}
        <div>
            <h2>{{ day.date.strftime('%A, %b %d, %Y') }}</h2>
            {% if day.lodging_banner %}
            <p>{{ day.lodging_banner }}</p>
            {% endif %}
            <ul>
                {% for time, label in day.events %}
                <li>{{ time.strftime('%-I:%M %p') }} - {{ label }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </body>
    </html>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(content)
        template_path = f.name
    
    yield template_path
    
    # Clean up
    if os.path.exists(template_path):
        os.unlink(template_path)


def test_adjust_timestamps_integration():
    """Test the integration of timestamp adjustment functionality."""
    # Sample trip data with Z-suffixed timestamps
    trip_data = {
        "trip": {
            "startDate": "2025-05-10T09:00:00Z",
            "endDate": "2025-05-15T17:00:00Z"
        },
        "transportations": [
            {
                "type": "flight",
                "origin": "JFK",
                "destination": "LAX",
                "departure": "2025-05-10T08:00:00Z",
                "arrival": "2025-05-10T11:00:00Z"
            }
        ]
    }
    
    # Adjust timestamps
    adjusted = adjust_incorrect_utc_timestamps(trip_data)
    
    # Parse dates using the adjusted data
    start, end = parse_dates(adjusted["trip"])
    
    # Verify dates are parsed correctly
    assert start.hour == 9  # Should preserve the original 09:00
    assert end.hour == 17   # Should preserve the original 17:00


def test_transport_events_with_adjusted_timestamps():
    """Test transport event formatting with adjusted timestamps."""
    # Create sample days for events
    start = datetime.fromisoformat("2025-05-10T00:00:00+00:00")
    end = datetime.fromisoformat("2025-05-12T00:00:00+00:00")
    
    from itinerary_generator.parser import build_days
    days = build_days(start, end)
    
    # Sample transportation data with Z-suffixed timestamps
    transportations = [
        {
            "type": "flight",
            "origin": "JFK",
            "destination": "LAX",
            "departure": "2025-05-10T08:00:00Z",
            "arrival": "2025-05-10T11:00:00Z"
        }
    ]
    
    # Adjust timestamps
    adjusted_transportations = adjust_incorrect_utc_timestamps({"transportations": transportations})["transportations"]
    
    # Format the transportation events with ET timezone
    tz = ZoneInfo("America/New_York")
    format_transport_events(days, adjusted_transportations, tz)
    
    # Verify events were added with the correct times
    assert len(days[0]["events"]) == 1
    event_time, event_label = days[0]["events"][0]
    
    # The event time should be exactly 8:00 AM, preserving the original input time
    assert event_time.hour == 8
    assert event_time.minute == 0
    
    # Should include flight info
    assert "✈️" in event_label
    assert "Flight from JFK to LAX" in event_label


def test_end_to_end_generate_itinerary(sample_trip_json, template_html):
    """Test end-to-end generation of an itinerary with timezone adjustments."""
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as output_file:
        output_html = output_file.name
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
        output_pdf = pdf_file.name
    
    try:
        # The issue is with how the mock is being handled. The pdf conversion is still 
        # trying to connect to a real URL. We need to patch at a deeper level to prevent
        # the actual request from being attempted.
        
        # First patch the renderer.convert_to_pdf function
        with patch('itinerary_generator.generate_itinerary.convert_to_pdf') as mock_pdf:
            mock_pdf.return_value = output_pdf
            
            # Generate the itinerary
            html_path, pdf_path = generate_itinerary(
                json_path=sample_trip_json,
                template_path=template_html,
                output_html=output_html,
                pdf_path=output_pdf,
                gotenberg_url="http://fake-gotenberg:3000",
                user_timezone="America/New_York"  # Use ET explicitly
            )
            
            # Verify outputs were created
            assert html_path == output_html
            assert pdf_path == output_pdf
            assert os.path.exists(html_path)
            
            # Verify mock was called
            mock_pdf.assert_called_once()
            
            # Read the generated HTML to verify content
            with open(html_path, 'r') as f:
                content = f.read()
                
                # Check timezone info is displayed correctly
                assert "Timezone: America/New_York" in content
                
                # Additional assertions about content can be added
                # but these might depend on the sample_trip_json content
    finally:
        # Clean up
        if os.path.exists(output_html):
            os.unlink(output_html)
        if os.path.exists(output_pdf):
            os.unlink(output_pdf)


def test_timezone_context_creation():
    """Test timezone info is correctly included in the template context."""
    # Sample trip data
    trip_data = {
        "trip": {
            "name": "Test Trip",
            "destinations": [{"timezone": "America/New_York"}]
        }
    }
    
    # Create sample days
    from itinerary_generator.parser import build_days
    start = datetime.fromisoformat("2025-05-10T00:00:00+00:00")
    end = datetime.fromisoformat("2025-05-12T00:00:00+00:00")
    days = build_days(start, end)
    
    # Create context
    context = create_template_context(trip_data, days)
    
    # Verify timezone information is in the context
    assert "timezone" in context
    assert context["timezone"] == "Local time at each location"


def test_timezone_difference_display():
    """Test timezone difference info is correctly generated."""
    # Mock the generate_itinerary function
    with patch('itinerary_generator.generate_itinerary.create_template_context') as mock_context:
        # Set up the mock to return a simple context
        mock_context.return_value = {"trip_name": "Test Trip"}
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file, \
             tempfile.NamedTemporaryFile(suffix='.html', delete=False) as template_file, \
             tempfile.NamedTemporaryFile(suffix='.html', delete=False) as output_file:
            
            json_path = json_file.name
            template_path = template_file.name
            output_html = output_file.name
            
            # Write a basic trip.json
            json_file.write(b'{"trip": {"name": "Test Trip", "startDate": "2025-05-10T00:00:00Z", "endDate": "2025-05-12T00:00:00Z", "destinations": [{"timezone": "Europe/Paris"}]}}')
            json_file.flush()
            
            # Use a non-destination timezone
            with patch('itinerary_generator.generate_itinerary.get_timezone_display_info') as mock_tz_info:
                mock_tz_info.return_value = {
                    "difference": 9,
                    "message": "The destination is 9 hours ahead of your timezone.",
                    "user_timezone": "America/Los_Angeles",
                    "destination_timezone": "Asia/Tokyo"
                }
                
                try:
                    # Generate itinerary with a different user timezone
                    generate_itinerary(
                        json_path=json_path,
                        template_path=template_path,
                        output_html=output_html,
                        user_timezone="America/Los_Angeles"
                    )
                    
                    # Verify timezone info was retrieved
                    mock_tz_info.assert_called_once()
                    args, kwargs = mock_tz_info.call_args
                    assert args[0] == "America/Los_Angeles"  # user timezone
                    assert args[1] == "Europe/Paris"         # destination timezone
                    
                    # Verify context was updated with timezone info
                    mock_context_calls = mock_context.call_args_list
                    for args, kwargs in mock_context_calls:
                        context = args[0]
                        if isinstance(context, dict) and "trip_name" in context:
                            assert context["timezone"] == "America/Los_Angeles"
                finally:
                    # Clean up
                    if os.path.exists(json_path):
                        os.unlink(json_path)
                    if os.path.exists(template_path):
                        os.unlink(template_path)
                    if os.path.exists(output_html):
                        os.unlink(output_html)