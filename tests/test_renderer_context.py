import pytest
from datetime import datetime

from itinerary_generator.renderer import create_template_context


def test_create_template_context_with_destination():
    """Test creating template context with destination information."""
    # Sample data with destination information
    trip_data = {
        "trip": {
            "name": "Summer Vacation",
            "destinations": [
                {
                    "name": "Testville",
                    "stateName": "Test State",
                    "countryName": "Test Country"
                }
            ],
            "notes": "<p>Test notes</p>"
        },
        "lodgings": [],
        "transportations": []
    }
    
    # Sample days
    days = [
        {
            "date": datetime.fromisoformat("2025-07-10T00:00:00+00:00"),
            "events": [],
            "lodging_banner": None
        },
        {
            "date": datetime.fromisoformat("2025-07-11T00:00:00+00:00"),
            "events": [],
            "lodging_banner": None
        }
    ]
    
    # Create context
    context = create_template_context(trip_data, days)
    
    # Check trip name and destination are different
    assert context["trip_name"] == "Summer Vacation"
    assert context["trip_destination"] == "Testville, Test State, Test Country"
    assert context["start_date"] == "Jul 10, 2025"
    assert context["end_date"] == "Jul 11, 2025"


def test_create_template_context_without_destination():
    """Test creating template context without destination information."""
    # Sample data without destinations
    trip_data = {
        "trip": {
            "name": "Business Trip",
            "destinations": [],
            "notes": ""
        }
    }
    
    # Sample days
    days = [
        {
            "date": datetime.fromisoformat("2025-08-01T00:00:00+00:00"),
            "events": [],
            "lodging_banner": None
        }
    ]
    
    # Create context
    context = create_template_context(trip_data, days)
    
    # Check destination is empty
    assert context["trip_name"] == "Business Trip"
    assert context["trip_destination"] == ""
    assert context["start_date"] == "Aug 01, 2025"