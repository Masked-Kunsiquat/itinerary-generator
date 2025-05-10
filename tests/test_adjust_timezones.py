"""
Test module for the adjust_incorrect_utc_timestamps function in generate_itinerary.py
"""
import pytest
import copy
from datetime import datetime

from itinerary_generator.generate_itinerary import adjust_incorrect_utc_timestamps


@pytest.fixture
def sample_trip_data():
    """Sample trip data with Z-suffixed timestamps."""
    return {
        "trip": {
            "name": "Test Trip",
            "startDate": "2025-05-10T09:00:00Z",
            "endDate": "2025-05-15T17:00:00Z",
            "destinations": [
                {"name": "New York", "timezone": "America/New_York"}
            ]
        },
        "lodgings": [
            {
                "name": "Test Hotel",
                "startDate": "2025-05-10T14:00:00Z",
                "endDate": "2025-05-15T10:00:00Z"
            }
        ],
        "transportations": [
            {
                "type": "flight",
                "origin": "JFK",
                "destination": "LAX",
                "departure": "2025-05-10T08:00:00Z",
                "arrival": "2025-05-10T11:00:00Z"
            },
            {
                "type": "car",
                "origin": "LAX",
                "destination": "Hotel",
                "departure": "2025-05-10T12:00:00Z",
                "arrival": "2025-05-10T13:00:00Z"
            }
        ],
        "activities": [
            {
                "name": "Museum Visit",
                "startDate": "2025-05-11T10:00:00Z"
            },
            {
                "name": "Dinner",
                "startDate": "2025-05-11T19:00:00Z"
            }
        ]
    }


def test_adjust_incorrect_utc_timestamps_preserves_original_data(sample_trip_data):
    """Test that adjust_incorrect_utc_timestamps doesn't modify the original data."""
    original = copy.deepcopy(sample_trip_data)
    
    # Call the function
    adjusted = adjust_incorrect_utc_timestamps(sample_trip_data)
    
    # Verify original data is unchanged
    assert sample_trip_data == original
    
    # Verify adjusted data is different
    assert adjusted != original


def test_adjust_incorrect_utc_timestamps_trip_dates(sample_trip_data):
    """Test adjustment of trip start/end dates."""
    adjusted = adjust_incorrect_utc_timestamps(sample_trip_data)
    
    # Verify Z suffix is removed from trip dates
    assert adjusted["trip"]["startDate"] == "2025-05-10T09:00:00"
    assert adjusted["trip"]["endDate"] == "2025-05-15T17:00:00"
    
    # Verify original Z suffix is preserved in the original data
    assert sample_trip_data["trip"]["startDate"].endswith("Z")
    assert sample_trip_data["trip"]["endDate"].endswith("Z")


def test_adjust_incorrect_utc_timestamps_lodgings(sample_trip_data):
    """Test adjustment of lodging dates."""
    adjusted = adjust_incorrect_utc_timestamps(sample_trip_data)
    
    # Verify Z suffix is removed from lodging dates
    assert adjusted["lodgings"][0]["startDate"] == "2025-05-10T14:00:00"
    assert adjusted["lodgings"][0]["endDate"] == "2025-05-15T10:00:00"


def test_adjust_incorrect_utc_timestamps_transportations(sample_trip_data):
    """Test adjustment of transportation dates."""
    adjusted = adjust_incorrect_utc_timestamps(sample_trip_data)
    
    # Verify Z suffix is removed from transportation dates
    assert adjusted["transportations"][0]["departure"] == "2025-05-10T08:00:00"
    assert adjusted["transportations"][0]["arrival"] == "2025-05-10T11:00:00"
    assert adjusted["transportations"][1]["departure"] == "2025-05-10T12:00:00"
    assert adjusted["transportations"][1]["arrival"] == "2025-05-10T13:00:00"


def test_adjust_incorrect_utc_timestamps_activities(sample_trip_data):
    """Test adjustment of activity dates."""
    adjusted = adjust_incorrect_utc_timestamps(sample_trip_data)
    
    # Verify Z suffix is removed from activity dates
    assert adjusted["activities"][0]["startDate"] == "2025-05-11T10:00:00"
    assert adjusted["activities"][1]["startDate"] == "2025-05-11T19:00:00"


def test_adjust_incorrect_utc_timestamps_with_non_z_dates():
    """Test adjustment when some dates don't have Z suffix."""
    # Create data with mixed date formats
    mixed_data = {
        "trip": {
            "startDate": "2025-05-10T09:00:00",  # No Z
            "endDate": "2025-05-15T17:00:00Z"    # With Z
        },
        "activities": [
            {
                "name": "Museum Visit",
                "startDate": "2025-05-11T10:00:00Z"  # With Z
            },
            {
                "name": "Dinner",
                "startDate": "2025-05-11T19:00:00"   # No Z
            }
        ]
    }
    
    adjusted = adjust_incorrect_utc_timestamps(mixed_data)
    
    # Verify dates without Z are unchanged
    assert adjusted["trip"]["startDate"] == "2025-05-10T09:00:00"
    assert adjusted["activities"][1]["startDate"] == "2025-05-11T19:00:00"
    
    # Verify Z suffix is removed where it existed
    assert adjusted["trip"]["endDate"] == "2025-05-15T17:00:00"
    assert adjusted["activities"][0]["startDate"] == "2025-05-11T10:00:00"


def test_adjust_incorrect_utc_timestamps_with_missing_dates():
    """Test adjustment with missing date fields."""
    # Create data with some missing dates
    incomplete_data = {
        "trip": {
            # Missing startDate
            "endDate": "2025-05-15T17:00:00Z"
        },
        "activities": [
            {
                "name": "Museum Visit"
                # Missing startDate
            }
        ]
    }
    
    # Should not raise exceptions for missing fields
    adjusted = adjust_incorrect_utc_timestamps(incomplete_data)
    
    # Verify adjustment of existing dates
    assert adjusted["trip"]["endDate"] == "2025-05-15T17:00:00"


def test_adjust_incorrect_utc_timestamps_with_empty_sections():
    """Test adjustment with empty sections."""
    # Create data with empty sections
    empty_sections_data = {
        "trip": {
            "startDate": "2025-05-10T09:00:00Z",
            "endDate": "2025-05-15T17:00:00Z"
        },
        "lodgings": [],
        "transportations": [],
        "activities": []
    }
    
    # Should handle empty sections gracefully
    adjusted = adjust_incorrect_utc_timestamps(empty_sections_data)
    
    # Verify adjustment of trip dates
    assert adjusted["trip"]["startDate"] == "2025-05-10T09:00:00"
    assert adjusted["trip"]["endDate"] == "2025-05-15T17:00:00"
    
    # Verify empty sections are preserved
    assert adjusted["lodgings"] == []
    assert adjusted["transportations"] == []
    assert adjusted["activities"] == []


def test_adjust_incorrect_utc_timestamps_with_missing_sections():
    """Test adjustment with missing sections."""
    # Create data with missing sections
    missing_sections_data = {
        "trip": {
            "startDate": "2025-05-10T09:00:00Z",
            "endDate": "2025-05-15T17:00:00Z"
        }
        # Missing lodgings, transportations, activities
    }
    
    # Should handle missing sections gracefully
    adjusted = adjust_incorrect_utc_timestamps(missing_sections_data)
    
    # Verify adjustment of trip dates
    assert adjusted["trip"]["startDate"] == "2025-05-10T09:00:00"
    assert adjusted["trip"]["endDate"] == "2025-05-15T17:00:00"