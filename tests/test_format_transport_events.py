import sys
import os
import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from itinerary_generator.parser import build_days
from itinerary_generator.formatting import format_transport_events


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


def test_format_transport_events_basic(sample_days, sample_timezone):
    """Test formatting basic transportation events."""
    transportations = [
        {
            "type": "flight",
            "origin": "JFK",
            "destination": "LAX",
            "departure": "2025-05-10T12:00:00Z",
            "arrival": "2025-05-10T15:00:00Z"
        }
    ]
    
    format_transport_events(sample_days, transportations, sample_timezone)
    
    # Check that event was added to the right day
    assert len(sample_days[0]["events"]) == 1
    
    # Check the event details
    event_time, event_label = sample_days[0]["events"][0]
    
    # Check that time is in local timezone (EDT is UTC-4)
    # 12:00 UTC should be 8:00 EDT
    assert event_time.hour == 8
    assert event_time.minute == 0
    
    # Check that label contains expected flight info
    assert "✈️" in event_label
    assert "Flight from JFK to LAX" in event_label


def test_format_transport_events_with_provider(sample_days, sample_timezone):
    """Test formatting transportation events with provider info."""
    transportations = [
        {
            "type": "flight",
            "origin": "JFK",
            "destination": "LHR",
            "departure": "2025-05-10T21:30:00Z",
            "arrival": "2025-05-11T09:30:00Z",
            "metadata": {"provider": "British Airways"},
            "confirmationCode": "BA1234"
        }
    ]
    
    format_transport_events(sample_days, transportations, sample_timezone)
    
    # Check that event was added
    assert len(sample_days[0]["events"]) == 1
    
    # Check the event details
    event_time, event_label = sample_days[0]["events"][0]
    
    # Check that label contains enhanced description
    assert "Flight from JFK to LHR via British Airways" in event_label
    assert "(#BA1234)" in event_label
    
    # Check that multi-day arrival info is included
    assert "arrives" in event_label
    assert "May 11" in event_label


def test_format_transport_events_train(sample_days, sample_timezone):
    """Test formatting train transportation events."""
    transportations = [
        {
            "type": "train",
            "origin": "London",
            "destination": "Paris",
            "departure": "2025-05-11T09:00:00Z",
            "arrival": "2025-05-11T12:30:00Z",
            "metadata": {"provider": "Eurostar"}
        }
    ]
    
    format_transport_events(sample_days, transportations, sample_timezone)
    
    # Check that event was added to the right day
    assert len(sample_days[1]["events"]) == 1
    
    # Check the event details
    event_time, event_label = sample_days[1]["events"][0]
    
    # Check that label contains train-specific formatting
    assert "🚆" in event_label
    assert "Train from London to Paris (Eurostar)" in event_label


def test_format_transport_events_car_types(sample_days, sample_timezone):
    """Test formatting different car transportation types."""
    transportations = [
        {
            "type": "car",
            "origin": "Airport",
            "destination": "Hotel",
            "departure": "2025-05-10T16:00:00Z",
            "arrival": "2025-05-10T17:00:00Z",
            "metadata": {"provider": "Rental"}
        },
        {
            "type": "car",
            "origin": "Hotel",
            "destination": "Restaurant",
            "departure": "2025-05-11T18:00:00Z",
            "arrival": "2025-05-11T18:30:00Z",
            "metadata": {"provider": "Uber"}
        }
    ]
    
    format_transport_events(sample_days, transportations, sample_timezone)
    
    # Check first day (rental car)
    assert len(sample_days[0]["events"]) == 1
    rental_time, rental_label = sample_days[0]["events"][0]
    assert "Drive rental car from Airport to Hotel" in rental_label
    
    # Check second day (Uber)
    assert len(sample_days[1]["events"]) == 1
    uber_time, uber_label = sample_days[1]["events"][0]
    assert "Uber from Hotel to Restaurant" in uber_label