import sys
import os
import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from itinerary_generator.formatting import get_transport_description


def test_flight_description():
    """Test flight description formatting."""
    # Basic flight
    flight = {
        "type": "flight",
        "origin": "JFK",
        "destination": "LAX"
    }
    description = get_transport_description(flight)
    assert description == "Flight from JFK to LAX"
    
    # Flight with airline
    flight_with_airline = {
        "type": "flight",
        "origin": "JFK",
        "destination": "LHR",
        "metadata": {"provider": "British Airways"}
    }
    description = get_transport_description(flight_with_airline)
    assert description == "Flight from JFK to LHR via British Airways"
    
    # Flight with confirmation code
    flight_with_confirmation = {
        "type": "flight",
        "origin": "SFO",
        "destination": "SEA",
        "confirmationCode": "ABC123",
        "metadata": {"provider": "Alaska Airlines"}
    }
    description = get_transport_description(flight_with_confirmation)
    assert description == "Flight from SFO to SEA via Alaska Airlines (#ABC123)"


def test_flight_with_complex_provider():
    """Test flight description with complex provider object."""
    flight = {
        "type": "flight",
        "origin": "ABC",
        "destination": "XYZ",
        "metadata": {
            "provider": {
                "code": "AL",
                "id": "fictional_id_123", 
                "logo": "https://example.com/logo.png",
                "name": "Example Airlines"
            },
            "reservation": "FICTIONAL"
        }
    }
    
    description = get_transport_description(flight)
    assert description == "Flight from ABC to XYZ via Example Airlines (#FICTIONAL)"
    
    # Test with code but no name
    flight["metadata"]["provider"] = {"code": "AL"}
    description = get_transport_description(flight)
    assert description == "Flight from ABC to XYZ via AL (#FICTIONAL)"


def test_train_description():
    """Test train description formatting."""
    # Basic train
    train = {
        "type": "train",
        "origin": "London",
        "destination": "Paris"
    }
    description = get_transport_description(train)
    assert description == "Train from London to Paris"
    
    # Train with provider
    train_with_provider = {
        "type": "train",
        "origin": "London",
        "destination": "Paris",
        "metadata": {"provider": "Eurostar"}
    }
    description = get_transport_description(train_with_provider)
    assert description == "Train from London to Paris (Eurostar)"


def test_car_description():
    """Test car description formatting based on provider."""
    # Self-driven car
    self_car = {
        "type": "car",
        "origin": "Home",
        "destination": "Airport",
        "metadata": {"provider": "Self"}
    }
    description = get_transport_description(self_car)
    assert description == "Drive from Home to Airport"
    
    # Rental car
    rental_car = {
        "type": "car",
        "origin": "Airport",
        "destination": "Hotel",
        "metadata": {"provider": "Rental"}
    }
    description = get_transport_description(rental_car)
    assert description == "Drive rental car from Airport to Hotel"
    
    # Rideshare
    uber = {
        "type": "car",
        "origin": "Hotel",
        "destination": "Restaurant",
        "metadata": {"provider": "Uber"}
    }
    description = get_transport_description(uber)
    assert description == "Uber from Hotel to Restaurant"


def test_other_transport_types():
    """Test other transportation types."""
    # Bus with provider
    bus = {
        "type": "bus",
        "origin": "Terminal",
        "destination": "City Center",
        "metadata": {"provider": "Metro Bus"}
    }
    description = get_transport_description(bus)
    assert description == "Bus from Terminal to City Center with Metro Bus"
    
    # Ferry with provider
    ferry = {
        "type": "ferry",
        "origin": "Mainland",
        "destination": "Island",
        "metadata": {"provider": "Island Ferry Co"}
    }
    description = get_transport_description(ferry)
    assert description == "Ferry from Mainland to Island with Island Ferry Co"
    
    # Unknown type
    unknown = {
        "type": "helicopter",
        "origin": "Helipad",
        "destination": "Resort"
    }
    description = get_transport_description(unknown)
    assert description == "Helicopter from Helipad to Resort"