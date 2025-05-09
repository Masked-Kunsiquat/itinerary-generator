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

import requests


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

import tempfile
from unittest.mock import patch, MagicMock
from generate_itinerary import (
    get_trip_timezone,
    convert_to_pdf,
    generate_itinerary,
)

def test_get_trip_timezone_fallback():
    assert get_trip_timezone({"destinations": []}) == "UTC"
    assert get_trip_timezone({"destinations": [{}]}) == "UTC"

def test_malformed_activity_is_skipped():
    days = build_days(*parse_dates(load_trip_data("static/trip.sample.json")["trip"]))
    tz = ZoneInfo("America/New_York")
    data = {
        "trip": {
            "startDate": "2025-05-10T00:00:00Z",
            "endDate": "2025-05-15T00:00:00Z",
            "destinations": [],
            "name": "Test Trip"
        },
        "activities": [{}]  # malformed: missing startDate
    }
    populate_days(days, data, tz)
    assert all("🎟️" not in label for day in days for _, label in day["events"])

@patch("generate_itinerary.requests.post")
def test_convert_to_pdf_success(mock_post, tmp_path):
    # mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"%PDF dummy content"
    mock_post.return_value = mock_response

    html_path = tmp_path / "sample.html"
    pdf_path = tmp_path / "output.pdf"

    html_path.write_text("<html><body>Test</body></html>")

    convert_to_pdf(str(html_path), str(pdf_path), "http://fake-gotenberg")

    assert pdf_path.exists()
    assert pdf_path.read_bytes().startswith(b"%PDF")

@patch("generate_itinerary.convert_to_pdf")
def test_generate_itinerary_runs_without_pdf(mock_convert, tmp_path):
    output_file = tmp_path / "itinerary.html"
    generate_itinerary(
        json_path="static/trip.sample.json",
        template_path="default-template.html",
        output_html=str(output_file)
    )
    assert output_file.exists()
    html = output_file.read_text()
    assert "<html" in html.lower()

@patch("generate_itinerary.requests.post")
def test_convert_to_pdf_raises_on_error(mock_post, tmp_path):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError("Gotenberg failed")
    mock_post.return_value = mock_response

    html_path = tmp_path / "fail.html"
    pdf_path = tmp_path / "fail.pdf"
    html_path.write_text("<html><body>Error</body></html>")

    with pytest.raises(requests.HTTPError, match="Gotenberg failed"):
        convert_to_pdf(str(html_path), str(pdf_path), "http://fake-gotenberg")

def test_main_cli_with_pdf(monkeypatch, tmp_path):
    output_html = tmp_path / "trip.html"
    output_pdf = tmp_path / "trip.pdf"

    monkeypatch.setattr(sys, "argv", [
        "generate_itinerary.py",
        "static/trip.sample.json",
        "default-template.html",
        str(output_html),
        "--pdf", str(output_pdf),
        "--gotenberg-url", "http://fake-gotenberg"
    ])

    with patch("generate_itinerary.convert_to_pdf") as mock_pdf:
        mock_pdf.return_value = None  # Don't actually run it
        from generate_itinerary import main
        main()
        assert output_html.exists()

def test_populate_days_address_edge_case():
    # Activity with address as "N/A" → should skip address logic
    data = {
        "trip": {
            "startDate": "2025-08-20T00:00:00Z",
            "endDate": "2025-08-21T00:00:00Z",
            "destinations": [],
            "name": "Edge Test"
        },
        "activities": [
            {
                "startDate": "2025-08-20T10:00:00Z",
                "name": "No Address Event",
                "address": "N/A"
            },
            {
                "startDate": "2025-08-20T12:00:00Z",
                "name": "Empty Address",
                "address": ""
            }
        ]
    }

    start, end = parse_dates(data["trip"])
    tz = ZoneInfo("UTC")
    days = build_days(start, end)
    populate_days(days, data, tz)

    # Make sure both events were added without crashing and without address suffix
    labels = [label for day in days for _, label in day["events"]]
    assert any("No Address Event" in l for l in labels)
    assert not any("@" in l for l in labels)  # no @address suffix
