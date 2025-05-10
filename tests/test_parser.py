import os
import json
import pytest
import tempfile
from datetime import datetime, timedelta, timezone # Added timezone from datetime
from zoneinfo import ZoneInfo

from itinerary_generator.parser import (
    load_trip_data,
    get_trip_timezone,
    parse_dates,
    build_days,
    get_common_timezones
)

# Path to the sample data for direct tests
SAMPLE_DATA_PATH = os.path.join("itinerary_generator", "data", "samples", "trip.sample.json")


@pytest.fixture
def sample_trip_data_for_parser(): # Renamed to avoid conflict if sample_trip_data is elsewhere
    """Sample trip data for parser testing."""
    with open(SAMPLE_DATA_PATH, "r") as f:
        return json.load(f)


def test_load_trip_data(sample_trip_data_for_parser): # Use the renamed fixture
    """Test loading trip data from a file."""
    # This test now effectively uses the fixture
    data = sample_trip_data_for_parser
    assert "trip" in data
    assert "lodgings" in data
    assert isinstance(data["transportations"], list)

def test_load_trip_data_file_not_found():
    """Test load_trip_data for FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Trip data file not found: non_existent_file.json"):
        load_trip_data("non_existent_file.json")

def test_load_trip_data_invalid_json_content():
    """Test load_trip_data with a file containing invalid JSON."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        tmp_file.write("{'this is not valid json',}") # Invalid JSON
        invalid_json_path = tmp_file.name
    
    try:
        with pytest.raises(json.JSONDecodeError) as excinfo:
            load_trip_data(invalid_json_path)
        assert "Invalid JSON in trip data file" in str(excinfo.value)
    finally:
        os.unlink(invalid_json_path)


def test_get_trip_timezone_with_destinations(sample_trip_data_for_parser): # Use renamed fixture
    """Test extracting timezone from trip with destinations."""
    tz = get_trip_timezone(sample_trip_data_for_parser["trip"])
    assert tz == "America/New_York"


def test_get_trip_timezone_no_destinations():
    """Test timezone fallback with no destinations."""
    tz = get_trip_timezone({"trip": {"destinations": []}}) # Encapsulate in "trip" if parser expects that
    assert tz == "UTC"
    tz_no_trip_key = get_trip_timezone({"destinations": []}) # Test original structure too
    assert tz_no_trip_key == "UTC"


def test_get_trip_timezone_no_timezone_in_destination():
    """Test timezone fallback when destination has no timezone."""
    tz = get_trip_timezone({"trip": {"destinations": [{"name": "Test"}]}})
    assert tz == "UTC"


def test_get_trip_timezone_malformed_destinations_structure():
    """Test get_trip_timezone when the destinations structure is unexpected."""
    assert get_trip_timezone({"trip": {"destinations": "not-a-list"}}) == "UTC"
    assert get_trip_timezone({"trip": {"destinations": [123]}}) == "UTC" # List contains non-dict
    assert get_trip_timezone({"trip": {"destinations": [{}]}}) == "UTC" # Dict missing 'timezone' key
    assert get_trip_timezone({"trip": {}}) == "UTC" # No destinations key
    assert get_trip_timezone({}) == "UTC" # Empty dict


def test_parse_dates(sample_trip_data_for_parser): # Use renamed fixture
    """Test parsing start and end dates from trip data."""
    start, end = parse_dates(sample_trip_data_for_parser["trip"])
    
    assert start.isoformat().startswith("2025-05-10")
    assert end.isoformat().startswith("2025-05-15")
    
    assert start.tzinfo is not None
    assert end.tzinfo is not None


def test_build_days_normal_range():
    """Test building day structures between dates."""
    # Use timezone.utc for tz-aware datetimes
    start = datetime(2025, 5, 10, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2025, 5, 15, 0, 0, 0, tzinfo=timezone.utc)
    
    days = build_days(start, end)
    
    assert len(days) == 6 
    
    for i, day in enumerate(days):
        assert "date" in day
        assert day["date"].date() == (start + timedelta(days=i)).date()
        assert "events" in day
        assert "lodging_banner" in day
        assert isinstance(day["events"], list)
        assert day["lodging_banner"] is None
    
    for i in range(len(days) - 1):
        assert (days[i+1]["date"].date() - days[i]["date"].date()) == timedelta(days=1)

def test_build_days_same_day():
    """Test build_days when start and end date are the same."""
    start = datetime(2025, 5, 10, 10, 0, 0, tzinfo=timezone.utc)
    end = datetime(2025, 5, 10, 14, 0, 0, tzinfo=timezone.utc)
    days = build_days(start, end)
    assert len(days) == 1
    assert days[0]["date"].date() == start.date()

def test_build_days_end_date_before_start_date():
    """Test build_days raises ValueError if end_date is before start_date."""
    start = datetime(2025, 5, 15, tzinfo=timezone.utc) # Use datetime.timezone.utc
    end = datetime(2025, 5, 10, tzinfo=timezone.utc)   # Use datetime.timezone.utc
    with pytest.raises(ValueError, match="End date cannot be before start date"):
        build_days(start, end)

def test_build_days_invalid_type():
    """Test build_days raises TypeError if inputs are not datetime objects."""
    with pytest.raises(TypeError, match="start_date and end_date must be datetime objects"):
        build_days("not-a-datetime", datetime(2025, 5, 10, tzinfo=timezone.utc))
    with pytest.raises(TypeError, match="start_date and end_date must be datetime objects"):
        build_days(datetime(2025, 5, 10, tzinfo=timezone.utc), "not-a-datetime")


def test_get_common_timezones():
    """Test that get_common_timezones returns a list of valid timezone strings."""
    timezones = get_common_timezones()
    assert isinstance(timezones, list)
    assert "UTC" in timezones
    assert "America/New_York" in timezones
    for tz_name in timezones:
        assert isinstance(tz_name, str)
        try:
            ZoneInfo(tz_name) # Check if it's a valid tz
        except Exception as e:
            pytest.fail(f"'{tz_name}' in get_common_timezones is not a valid timezone: {e}")