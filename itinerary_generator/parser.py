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
        
    Raises:
        FileNotFoundError: If the specified file does not exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Trip data file not found: {path}") from None
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in trip data file: {e.msg}", e.doc, e.pos) from e


def get_trip_timezone(trip):
    """
    Extract timezone from trip destinations or fallback to UTC.
    
    Args:
        trip (dict): Trip data with destinations
        
    Returns:
        str: Timezone string (e.g., 'America/New_York') or 'UTC'
    """
    try:
        if not trip.get("destinations"):
            return "UTC"
        
        timezone = trip["destinations"][0].get("timezone")
        return timezone if timezone else "UTC"
    except (IndexError, KeyError, TypeError):
        # Fallback to UTC in case of any issues with the data structure
        return "UTC"


def parse_dates(trip):
    """
    Parse start and end dates from trip data.
    
    Args:
        trip (dict): Trip data containing startDate and endDate
        
    Returns:
        tuple: (start_date, end_date) as datetime objects with timezone info
        
    Raises:
        KeyError: If required date fields are missing
        ValueError: If dates are in an invalid format
    """
    try:
        # Convert ISO format strings to datetime objects
        # When the 'Z' is present, it denotes UTC time
        # Replace with +00:00 to make it timezone-aware
        start = datetime.fromisoformat(trip["startDate"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(trip["endDate"].replace("Z", "+00:00"))
        return start, end
    except KeyError as e:
        # Specific error for missing required fields
        raise KeyError(f"Trip data missing required date field: {e}") from e
    except ValueError as e:
        # Handle date parsing errors
        raise ValueError(f"Invalid date format in trip data: {e}") from e


def build_days(start_date, end_date):
    """
    Build a list of day structures between start and end dates.
    
    Args:
        start_date (datetime): Trip start date
        end_date (datetime): Trip end date
        
    Returns:
        list: List of day dictionaries, each with date, events, and lodging_banner
    """
    if end_date < start_date:
        raise ValueError("End date cannot be before start date")
        
    days = []
    for i in range((end_date - start_date).days + 1):
        current = start_date + timedelta(days=i)
        days.append({
            "date": current,
            "events": [],
            "lodging_banner": None
        })
    return days