"""
Parser module for loading and structuring Surmai trip data.
"""
from datetime import datetime, timedelta
import json
from zoneinfo import ZoneInfo


def load_trip_data(path):
    """
    Load and parse a Surmai trip.json file.
    
    Args:
        path (str): Path to the JSON file
        
    Returns:
        dict: Parsed trip data
    """
    with open(path, "r") as f:
        return json.load(f)


def get_trip_timezone(trip):
    """
    Extract timezone from trip destinations or fallback to UTC.
    
    Args:
        trip (dict): Trip data with destinations
        
    Returns:
        str: Timezone string (e.g., 'America/New_York') or 'UTC'
    """
    return trip["destinations"][0].get("timezone", "UTC") if trip["destinations"] else "UTC"


def parse_dates(trip):
    """
    Parse start and end dates from trip data.
    
    Args:
        trip (dict): Trip data containing startDate and endDate
        
    Returns:
        tuple: (start_date, end_date) as datetime objects with timezone info
    """
    start = datetime.fromisoformat(trip["startDate"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(trip["endDate"].replace("Z", "+00:00"))
    return start, end


def build_days(start_date, end_date):
    """
    Build a list of day structures between start and end dates.
    
    Args:
        start_date (datetime): Trip start date
        end_date (datetime): Trip end date
        
    Returns:
        list: List of day dictionaries, each with date, events, and lodging_banner
    """
    days = []
    for i in range((end_date - start_date).days + 1):
        current = start_date + timedelta(days=i)
        days.append({
            "date": current,
            "events": [],
            "lodging_banner": None
        })
    return days