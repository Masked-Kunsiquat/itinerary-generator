"""
Surmai Itinerary Generator

A tool for rendering beautiful, print-ready trip itineraries
from Surmai's `trip.json` exports using customizable templates.
"""

# Import key functions for easy access
from .parser import load_trip_data, parse_dates, build_days
from .formatting import populate_days, get_transport_icon
from .renderer import render_itinerary, convert_to_pdf
from .generate_itinerary import generate_itinerary
from .time_utils import format_date, format_time, convert_to_timezone

__version__ = "1.0.1"