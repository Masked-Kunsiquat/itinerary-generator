import sys
import os
import json
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from itinerary_generator.parser import load_trip_data, get_trip_timezone, parse_dates, build_days

# Path to the sample data for direct tests
SAMPLE_DATA_PATH = os.path.join("itinerary_generator", "data", "samples", "trip.sample.json")


@pytest.fixture
def sample_trip_data():
    """Sample trip data for testing."""
    with open(SAMPLE_DATA_PATH, "r") as f:
        return json.load(f)


def test_load_trip_data():
    """Test loading trip data from a file."""
    data = load_trip_data(SAMPLE_DATA_PATH)
    assert "trip" in data
    assert "lodgings" in data
    assert isinstance(data["transportations"], list)


def test_get_trip_timezone_with_destinations(sample_trip_data):
    """Test extracting timezone from trip with destinations."""
    tz = get_trip_timezone(sample_trip_data["trip"])
    assert tz == "America/New_York"


def test_get_trip_timezone_no_destinations():
    """Test timezone fallback with no destinations."""
    tz = get_trip_timezone({"destinations": []})
    assert tz == "UTC"


def test_get_trip_timezone_no_timezone_in_destination():
    """Test timezone fallback when destination has no timezone."""
    tz = get_trip_timezone({"destinations": [{"name": "Test"}]})
    assert tz == "UTC"


def test_parse_dates(sample_trip_data):
    """Test parsing start and end dates from trip data."""
    start, end = parse_dates(sample_trip_data["trip"])
    
    # Check the correct dates were parsed
    assert start.isoformat().startswith("2025-05-10")
    assert end.isoformat().startswith("2025-05-15")
    
    # Check timezone awareness
    assert start.tzinfo is not None
    assert end.tzinfo is not None


def test_build_days():
    """Test building day structures between dates."""
    start = datetime.fromisoformat("2025-05-10T00:00:00+00:00")
    end = datetime.fromisoformat("2025-05-15T00:00:00+00:00")
    
    days = build_days(start, end)
    
    # Check correct number of days
    assert len(days) == 6
    
    # Check day structure
    for day in days:
        assert "date" in day
        assert "events" in day
        assert "lodging_banner" in day
        assert isinstance(day["events"], list)
        assert day["lodging_banner"] is None
    
    # Check days are in sequence
    for i in range(len(days) - 1):
        assert days[i+1]["date"] - days[i]["date"] == timedelta(days=1)