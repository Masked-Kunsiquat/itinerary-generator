import sys
import os
import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from itinerary_generator.parser import build_days, parse_dates
from itinerary_generator.formatting import (
    insert_event, get_transport_icon, format_lodging_events,
    format_transport_events, format_activity_events, populate_days
)


@pytest.fixture
def sample_days():
    """Sample days for testing."""
    start = datetime.fromisoformat("2025-05-10T00:00:00+00:00")
    end = datetime.fromisoformat("2025-05-12T00:00:00+00:00")
    return build_days(start, end)


@pytest.fixture
def sample_timezone():
    """Sample timezone for testing."""
    return ZoneInfo("America/New_York")


def test_insert_event(sample_days, sample_timezone):
    """Test inserting an event into the appropriate day."""
    event_time = datetime.fromisoformat("2025-05-11T14:30:00+00:00")
    label = "Test Event"
    
    insert_event(sample_days, event_time, sample_timezone, label)
    
    # Event should be in the second day (May 11)
    assert len(sample_days[0]["events"]) == 0
    assert len(sample_days[1]["events"]) == 1
    assert len(sample_days[2]["events"]) == 0
    
    # Check the event details
    event_time_local, event_label = sample_days[1]["events"][0]
    assert event_label == label
    
    # Local time should be in America/New_York timezone (UTC-4 during DST)
    assert event_time_local.hour == 10  # 14:30 UTC -> 10:30 EDT


def test_get_transport_icon():
    """Test mapping transport types to emoji icons."""
    assert get_transport_icon("flight") == "✈️"
    assert get_transport_icon("train") == "🚆"
    assert get_transport_icon("bus") == "🚌"
    assert get_transport_icon("car") == "🚗"
    
    # Unknown transport type should default to car
    assert get_transport_icon("unknown") == "🚗"
    
    # Case insensitive
    assert get_transport_icon("FLIGHT") == "✈️"


def test_format_lodging_events(sample_days, sample_timezone):
    """Test formatting lodging check-in/out events and banners."""
    lodgings = [
        {
            "name": "Test Hotel",
            "startDate": "2025-05-10T14:00:00Z",  # Check-in day 1
            "endDate": "2025-05-12T10:00:00Z"     # Check-out day 3
        }
    ]
    
    format_lodging_events(sample_days, lodgings, sample_timezone)
    
    # Day 1: Check-in event
    assert len(sample_days[0]["events"]) == 1
    assert "Check-In at Test Hotel" in sample_days[0]["events"][0][1]
    
    # Day 2: Should have lodging banner
    assert sample_days[1]["lodging_banner"] is not None
    assert "Staying at Test Hotel" in sample_days[1]["lodging_banner"]
    
    # Day 3: Check-out event
    assert len(sample_days[2]["events"]) == 1
    assert "Check-Out from Test Hotel" in sample_days[2]["events"][0][1]


def test_format_transport_events(sample_days, sample_timezone):
    """Test formatting transportation events."""
    transportations = [
        {
            "type": "flight",
            "origin": "JFK",
            "destination": "LAX",
            "departure": "2025-05-10T08:00:00Z",
            "arrival": "2025-05-10T11:00:00Z"
        },
        {
            # Multi-day transport
            "type": "car",
            "origin": "LAX",
            "destination": "SFO",
            "departure": "2025-05-11T20:00:00Z",
            "arrival": "2025-05-12T04:00:00Z"
        }
    ]
    
    format_transport_events(sample_days, transportations, sample_timezone)
    
    # Day 1: Flight
    assert len(sample_days[0]["events"]) == 1
    assert "✈️" in sample_days[0]["events"][0][1]
    assert "JFK to LAX" in sample_days[0]["events"][0][1]
    
    # Day 2: Car (multi-day)
    assert len(sample_days[1]["events"]) == 1
    assert "🚗" in sample_days[1]["events"][0][1]
    assert "LAX to SFO" in sample_days[1]["events"][0][1]
    assert "arrives" in sample_days[1]["events"][0][1]  # Shows arrival info for multi-day


def test_format_activity_events(sample_days, sample_timezone):
    """Test formatting activity events."""
    activities = [
        {
            "name": "Museum Visit",
            "address": "123 Museum St",
            "startDate": "2025-05-10T13:00:00Z"
        },
        {
            "name": "No Address Activity",
            "startDate": "2025-05-11T15:00:00Z"
        },
        {
            "name": "N/A Address",
            "address": "N/A",
            "startDate": "2025-05-11T17:00:00Z"
        },
        # Malformed activity (missing startDate)
        {
            "name": "Bad Activity"
        }
    ]
    
    format_activity_events(sample_days, activities, sample_timezone)
    
    # Day 1: Museum with address
    assert len(sample_days[0]["events"]) == 1
    assert "Museum Visit" in sample_days[0]["events"][0][1]
    assert "@ 123 Museum St" in sample_days[0]["events"][0][1]
    
    # Day 2: Two valid activities (no address and N/A address)
    assert len(sample_days[1]["events"]) == 2
    assert any("No Address Activity" in e[1] for e in sample_days[1]["events"])
    assert any("N/A Address" in e[1] for e in sample_days[1]["events"])
    assert not any("@ N/A" in e[1] for e in sample_days[1]["events"])  # N/A address should be skipped


def test_populate_days(sample_days, sample_timezone):
    """Test populating days with all event types."""
    data = {
        "lodgings": [
            {
                "name": "Test Hotel",
                "startDate": "2025-05-10T14:00:00Z",
                "endDate": "2025-05-12T10:00:00Z"
            }
        ],
        "transportations": [
            {
                "type": "flight",
                "origin": "JFK",
                "destination": "LAX",
                "departure": "2025-05-10T08:00:00Z",
                "arrival": "2025-05-10T11:00:00Z"
            }
        ],
        "activities": [
            {
                "name": "Museum Visit",
                "address": "123 Museum St",
                "startDate": "2025-05-11T13:00:00Z"
            }
        ]
    }
    
    populate_days(sample_days, data, sample_timezone)
    
    # Check that all events were added
    assert len(sample_days[0]["events"]) == 2  # Flight and check-in
    assert len(sample_days[1]["events"]) == 1  # Museum
    assert len(sample_days[2]["events"]) == 1  # Check-out
    
    # Check events are sorted by time
    for day in sample_days:
        times = [event[0] for event in day["events"]]
        assert times == sorted(times)