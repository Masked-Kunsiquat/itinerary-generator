import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pytest
from generate_itinerary import (
    load_trip_data,
    parse_dates,
    build_days,
    populate_days,
)

@pytest.fixture
def trip_data():
    with open("static/trip.sample.json", "r") as f:
        return json.load(f)

def test_load_trip_data():
    data = load_trip_data("static/trip.sample.json")
    assert "trip" in data
    assert "lodgings" in data
    assert isinstance(data["transportations"], list)

def test_parse_dates(trip_data):
    start, end = parse_dates(trip_data["trip"])
    assert start.isoformat().startswith("2025-05-10")
    assert end.isoformat().startswith("2025-05-15")

def test_build_days_and_populate(trip_data):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/New_York")
    start, end = parse_dates(trip_data["trip"])
    days = build_days(start, end)
    populate_days(days, trip_data, tz)
    assert len(days) == 6  # 6 days total
    assert any("Check-In" in label for _, label in days[0]["events"])
    assert any("🎟️" in label for d in days for _, label in d["events"])  # At least one activity
