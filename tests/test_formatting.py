import pytest
from datetime import datetime, timezone, time # Added time
from zoneinfo import ZoneInfo

from itinerary_generator.parser import build_days
from itinerary_generator.formatting import (
    insert_event, get_transport_icon, format_lodging_events,
    format_transport_events, format_activity_events, populate_days,
    get_transport_description # Explicitly import this
)

@pytest.fixture
def sample_days_fixture():
    """Sample days for testing."""
    start = datetime(2025, 5, 10, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2025, 5, 12, 0, 0, 0, tzinfo=timezone.utc)
    return build_days(start, end)

@pytest.fixture
def sample_timezone_fixture():
    """Sample timezone for testing."""
    return ZoneInfo("America/New_York")

# --- Tests for insert_event ---
def test_insert_event_basic(sample_days_fixture, sample_timezone_fixture):
    """Test inserting a timezone-aware event."""
    days = [day.copy() for day in sample_days_fixture]
    event_dt = datetime(2025, 5, 11, 14, 30, 0, tzinfo=timezone.utc) # 10:30 AM ET
    label = "Aware Event"
    insert_event(days, event_dt, sample_timezone_fixture, label)
    
    day_11 = next(d for d in days if d["date"].day == 11)
    assert (time(10, 30), label) in day_11["events"]

def test_insert_event_with_naive_datetime(sample_days_fixture, sample_timezone_fixture):
    """Test inserting an event with a naive datetime (should assume ET)."""
    days = [day.copy() for day in sample_days_fixture]
    naive_event_time = datetime(2025, 5, 11, 10, 30) 
    label = "Naive Test Event Label"
    
    day_to_check = next(d for d in days if d["date"].date() == naive_event_time.date())
    initial_event_count = len(day_to_check["events"])

    insert_event(days, naive_event_time, sample_timezone_fixture, label)
    
    assert len(day_to_check["events"]) == initial_event_count + 1
    event_time_local, event_label_text = day_to_check["events"][-1]
    
    assert event_label_text == label
    assert event_time_local.hour == 10
    assert event_time_local.minute == 30

# --- Tests for get_transport_icon ---
def test_get_transport_icon_known_types():
    assert get_transport_icon("flight") == "✈️"
    assert get_transport_icon("train") == "🚆"

def test_get_transport_icon_unknown_type():
    assert get_transport_icon("blimp") == "🚗" # Default

def test_get_transport_icon_case_insensitive():
    assert get_transport_icon("FlIgHt") == "✈️"

def test_get_transport_icon_non_string_type():
    assert get_transport_icon(123) == "🚗" 
    assert get_transport_icon(None) == "🚗"

# --- Tests for format_lodging_events ---
def test_format_lodging_events_basic(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    lodgings = [{"name": "Test Hotel", "startDate": "2025-05-10T14:00:00Z", "endDate": "2025-05-12T10:00:00Z"}]
    format_lodging_events(days, lodgings, sample_timezone_fixture)
    
    day_10_events = next(d for d in days if d["date"].day == 10)["events"]
    day_11_banner = next(d for d in days if d["date"].day == 11)["lodging_banner"]
    day_12_events = next(d for d in days if d["date"].day == 12)["events"]

    assert any("Check-In at Test Hotel" in e[1] for e in day_10_events)
    assert "Staying at Test Hotel" in day_11_banner
    assert any("Check-Out from Test Hotel" in e[1] for e in day_12_events)

def test_format_lodging_events_malformed_date_string(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    lodgings = [
        {"name": "Valid Hotel", "startDate": "2025-05-10T14:00:00Z", "endDate": "2025-05-11T10:00:00Z"},
        {"name": "Bad Date Hotel", "startDate": "this-is-not-a-date", "endDate": "2025-05-12T10:00:00Z"}
    ]
    format_lodging_events(days, lodgings, sample_timezone_fixture)
    assert any("Valid Hotel" in e[1] for day_events in [d["events"] for d in days] for e in day_events)
    assert not any("Bad Date Hotel" in e[1] for day_events in [d["events"] for d in days] for e in day_events)


def test_format_lodging_events_missing_date_key(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    lodgings = [
        {"name": "Valid Hotel", "startDate": "2025-05-10T14:00:00Z", "endDate": "2025-05-11T10:00:00Z"},
        {"name": "Missing Date Hotel", "address": "Some Address"} 
    ]
    format_lodging_events(days, lodgings, sample_timezone_fixture)
    assert any("Valid Hotel" in e[1] for day_events in [d["events"] for d in days] for e in day_events)
    assert not any("Missing Date Hotel" in e[1] for day_events in [d["events"] for d in days] for e in day_events)

def test_format_lodging_events_missing_name_key(sample_days_fixture, sample_timezone_fixture):
    """Test that missing 'name' in lodging causes skip via KeyError in try-except."""
    days = [d.copy() for d in sample_days_fixture]
    lodgings = [{"startDate": "2025-05-10T14:00:00Z", "endDate": "2025-05-11T10:00:00Z"}] # No name
    # Count total events before
    total_events_before = sum(len(d["events"]) for d in days)
    format_lodging_events(days, lodgings, sample_timezone_fixture)
    # No new events should be added
    total_events_after = sum(len(d["events"]) for d in days)
    assert total_events_after == total_events_before


# --- Tests for get_transport_description ---
def test_get_transport_description_missing_fields():
    assert get_transport_description({"type": "flight", "origin": "AAA", "destination": "BBB"}) == "Flight from AAA to BBB"
    assert get_transport_description({}) == "Unknown from Unknown Origin to Unknown Destination"

def test_get_transport_description_generic_with_provider():
    transport = {"type": "Helicopter", "origin": "Rooftop", "destination": "Island", "metadata": {"provider": "Heli Adventures"}}
    assert get_transport_description(transport) == "Helicopter from Rooftop to Island with Heli Adventures"

def test_get_transport_description_car_with_other_provider():
    transport = {"type": "car", "origin": "City A", "destination": "City B", "metadata": {"provider": "My Own Car Service"}}
    assert get_transport_description(transport) == "Car from City A to City B with My Own Car Service"

def test_get_transport_description_car_no_provider():
    transport = {"type": "car", "origin": "A", "destination": "B"}
    assert get_transport_description(transport) == "Car from A to B"


# --- Tests for format_transport_events ---
def test_format_transport_events_basic_flight(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    transportations = [{"type": "flight", "origin": "JFK", "destination": "LAX", "departure": "2025-05-10T12:00:00Z", "arrival": "2025-05-10T15:00:00Z"}] # 8 AM ET departure
    format_transport_events(days, transportations, sample_timezone_fixture)
    day_10_events = next(d for d in days if d["date"].day == 10)["events"]
    assert any("✈️ 8:00 AM — Flight from JFK to LAX (arrives 11:00 AM)" in e[1] for e in day_10_events)


def test_format_transport_events_skips_missing_departure(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    transportations = [{"type": "flight", "origin": "JFK", "destination": "LAX", "arrival": "2025-05-10T11:00:00Z"}]
    day_to_check = next(d for d in days if d["date"].date() == datetime(2025,5,10).date())
    initial_event_count = len(day_to_check["events"])
    format_transport_events(days, transportations, sample_timezone_fixture)
    assert len(day_to_check["events"]) == initial_event_count

def test_format_transport_events_handles_missing_arrival(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    transportations = [{"type": "car", "origin": "Hotel", "destination": "Restaurant", "departure": "2025-05-10T18:00:00Z", "metadata": {"provider": "Self"}}] # 2 PM ET
    day_to_check = next(d for d in days if d["date"].date() == datetime(2025,5,10).date())
    initial_event_count = len(day_to_check["events"])
    format_transport_events(days, transportations, sample_timezone_fixture)
    assert len(day_to_check["events"]) == initial_event_count + 1
    assert "🚗 2:00 PM — Drive from Hotel to Restaurant" in day_to_check["events"][-1][1]
    assert "arrives" not in day_to_check["events"][-1][1]

def test_format_transport_events_skips_invalid_date_string(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    transportations = [{"type": "flight", "origin": "JFK", "destination": "LAX", "departure": "not-a-valid-date", "arrival": "2025-05-10T11:00:00Z"}]
    day_to_check = next(d for d in days if d["date"].date() == datetime(2025,5,10).date())
    initial_event_count = len(day_to_check["events"])
    format_transport_events(days, transportations, sample_timezone_fixture)
    assert len(day_to_check["events"]) == initial_event_count

# --- Tests for format_activity_events ---
def test_format_activity_events_basic(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    activities = [{"name": "Museum Visit", "address": "123 Main St", "startDate": "2025-05-10T17:00:00Z"}] # 1 PM ET
    format_activity_events(days, activities, sample_timezone_fixture)
    day_10_events = next(d for d in days if d["date"].day == 10)["events"]
    assert any("🎟️ 1:00 PM — Museum Visit @ 123 Main St" in e[1] for e in day_10_events)

def test_format_activity_events_invalid_date_string_format(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    activities = [{"name": "Activity With Bad Date", "startDate": "definitely-not-a-date"}]
    day_to_check = next(d for d in days if d["date"].date() == datetime(2025,5,10).date())
    initial_event_count = len(day_to_check["events"])
    format_activity_events(days, activities, sample_timezone_fixture)
    assert len(day_to_check["events"]) == initial_event_count
    assert not any("Activity With Bad Date" in e[1] for e in day_to_check["events"])

def test_format_activity_events_missing_start_date(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    activities = [{"name": "Activity No Date"}] 
    day_to_check = next(d for d in days if d["date"].date() == datetime(2025,5,10).date())
    initial_event_count = len(day_to_check["events"])
    format_activity_events(days, activities, sample_timezone_fixture)
    assert len(day_to_check["events"]) == initial_event_count
    assert not any("Activity No Date" in e[1] for e in day_to_check["events"])

def test_format_activity_events_address_variations(sample_days_fixture, sample_timezone_fixture):
    days = [d.copy() for d in sample_days_fixture]
    activities = [
        {"name": "Event No Address", "startDate": "2025-05-10T18:00:00Z"}, # 2 PM ET
        {"name": "Event N/A Address", "startDate": "2025-05-10T19:00:00Z", "address": "N/A"}, # 3 PM ET
        {"name": "Event Empty Address", "startDate": "2025-05-10T20:00:00Z", "address": "  "}, # 4 PM ET
    ]
    format_activity_events(days, activities, sample_timezone_fixture)
    day_10_events = next(d for d in days if d["date"].day == 10)["events"]
    
    labels = [e[1] for e in day_10_events]
    assert any("🎟️ 2:00 PM — Event No Address" == lbl for lbl in labels if "Event No Address" in lbl)
    assert any("🎟️ 3:00 PM — Event N/A Address" == lbl for lbl in labels if "Event N/A Address" in lbl)
    assert any("🎟️ 4:00 PM — Event Empty Address" == lbl for lbl in labels if "Event Empty Address" in lbl)


# --- Test for populate_days ---
def test_populate_days_all_event_types(sample_days_fixture, sample_timezone_fixture):
    """Test populating days with all event types and sorting."""
    days = [d.copy() for d in sample_days_fixture] # Operate on a copy
    data = {
        "lodgings": [
            {"name": "Grand Hotel", "startDate": "2025-05-10T16:00:00Z", "endDate": "2025-05-12T10:00:00Z"} # Check-in 12 PM ET
        ],
        "transportations": [ # Flight 8 AM ET
            {"type": "flight", "origin": "JFK", "destination": "LAX", "departure": "2025-05-10T12:00:00Z", "arrival": "2025-05-10T15:00:00Z"}
        ],
        "activities": [ # Museum 11 AM ET
            {"name": "Early Museum", "address": "456 Art Ave", "startDate": "2025-05-10T15:00:00Z"}
        ]
    }
    
    populate_days(days, data, sample_timezone_fixture)
    
    day_10_events = next(d for d in days if d["date"].day == 10)["events"]
    
    # Expected order on May 10th for ET (sample_timezone_fixture):
    # 1. Flight @ 8:00 AM
    # 2. Early Museum @ 11:00 AM
    # 3. Check-In @ 12:00 PM
    
    assert len(day_10_events) == 3
    assert "✈️ 8:00 AM" in day_10_events[0][1]
    assert "🎟️ 11:00 AM — Early Museum" in day_10_events[1][1]
    assert "🛏 12:00 PM — Check-In at Grand Hotel" in day_10_events[2][1]

    # Check another day for lodging banner
    day_11_banner = next(d for d in days if d["date"].day == 11)["lodging_banner"]
    assert "Staying at Grand Hotel" in day_11_banner