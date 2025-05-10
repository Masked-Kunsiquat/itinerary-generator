# itinerary_generator/parser.py
"""
Parser module for loading and structuring Surmai trip data.
"""
from datetime import datetime, timedelta
import json
import os
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


def get_trip_timezone(trip, user_timezone=None):
    """
    Get timezone from user preference, environment, trip destinations or fallback to UTC.
    
    Priority:
    1. User-provided timezone (if valid)
    2. Environment variable TZ
    3. Trip destination timezone
    4. UTC fallback
    
    Args:
        trip (dict): Trip data with destinations
        user_timezone (str, optional): User-specified timezone
        
    Returns:
        str: Timezone string (e.g., 'America/New_York') or 'UTC'
    """
    # Priority 1: Use user-provided timezone if valid
    if user_timezone:
        try:
            ZoneInfo(user_timezone)
            return user_timezone
        except Exception:
            pass # Invalid timezone provided, fall through
    
    # Priority 2: Use environment variable TZ if available
    env_tz = os.environ.get('TZ')
    if env_tz:
        try:
            ZoneInfo(env_tz)
            return env_tz
        except Exception:
            pass # Invalid timezone in environment, fall through
    
    # Priority 3: Extract from trip destinations
    try:
        if trip.get("destinations") and isinstance(trip["destinations"], list) and len(trip["destinations"]) > 0:
            first_destination = trip["destinations"][0]
            if isinstance(first_destination, dict): # Check if the first destination is a dictionary
                timezone_str = first_destination.get("timezone")
                if timezone_str:
                    try:
                        ZoneInfo(timezone_str)
                        return timezone_str
                    except Exception:
                        pass # Invalid timezone in trip data, fall through
    except (IndexError, KeyError, TypeError):
        # This block handles issues if "destinations" is not a list,
        # or an item in it is not a dict, or other structural issues.
        pass
        
    # Priority 4: Fallback to UTC
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
        start_str = trip["startDate"]
        end_str = trip["endDate"]
        
        if start_str.endswith("Z"):
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        else:
            et_tz = ZoneInfo("America/New_York") # Defined locally to avoid repeated import unless necessary
            start = datetime.fromisoformat(start_str).replace(tzinfo=et_tz)
        
        if end_str.endswith("Z"):
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        else:
            et_tz = ZoneInfo("America/New_York") # Defined locally
            end = datetime.fromisoformat(end_str).replace(tzinfo=et_tz)
            
        return start, end
    except KeyError as e:
        raise KeyError(f"Trip data missing required date field: {e}") from e
    except ValueError as e:
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
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        raise TypeError("start_date and end_date must be datetime objects")

    if end_date < start_date:
        raise ValueError("End date cannot be before start date")
        
    days = []
    current_date_tracker = start_date
    while current_date_tracker.date() <= end_date.date():
        days.append({
            "date": current_date_tracker,
            "events": [],
            "lodging_banner": None
        })
        current_date_tracker += timedelta(days=1)
    return days


def get_common_timezones():
    """
    Return a list of common timezones for UI display.
    
    Returns:
        list: List of common timezone strings
    """
    common_timezones = [
        "UTC", "America/New_York", "America/Chicago", "America/Denver",
        "America/Los_Angeles", "Europe/London", "Europe/Paris", "Europe/Berlin",
        "Asia/Tokyo", "Asia/Singapore", "Australia/Sydney", "Pacific/Auckland"
    ]
    
    valid_timezones = []
    for tz_name in common_timezones:
        try:
            ZoneInfo(tz_name)
            valid_timezones.append(tz_name)
        except Exception:  # pragma: no cover
            # This block is for the unlikely event of a typo in the hardcoded list above.
            pass 
    return valid_timezones