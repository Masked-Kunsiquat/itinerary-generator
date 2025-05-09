import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pytest
from zoneinfo import ZoneInfo

from app import app as flask_app
from generate_itinerary import (
    load_trip_data,
    parse_dates,
    build_days,
    populate_days,
    render_itinerary,
)


@pytest.fixture
def trip_data():
    with open("static/trip.sample.json", "r") as f:
        return json.load(f)
    
@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()

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

def test_render_itinerary(tmp_path, trip_data):
    from zoneinfo import ZoneInfo
    start, end = parse_dates(trip_data["trip"])
    tz = ZoneInfo("America/New_York")
    days = build_days(start, end)
    populate_days(days, trip_data, tz)

    context = {
        "trip_name": trip_data["trip"]["name"],
        "start_date": start.strftime("%b %d, %Y"),
        "end_date": end.strftime("%b %d, %Y"),
        "days": days,
        "trip_notes": trip_data["trip"].get("notes", ""),
        "lodgings": trip_data.get("lodgings", []),
        "transportations": trip_data.get("transportations", [])
    }

    output_file = tmp_path / "rendered.html"
    html_path = render_itinerary("default-template.html", context, str(output_file))

    assert os.path.exists(html_path)
    with open(html_path) as f:
        html = f.read()
        assert "Sample Adventure" in html
        assert "Check-In" in html or "Check-Out" in html
        assert "<html" in html.lower()

def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Generate Trip Itinerary" in response.data
