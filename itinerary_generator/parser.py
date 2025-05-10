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
            # Validate the timezone
            ZoneInfo(user_timezone)
            return user_timezone
        except Exception:
            # Invalid timezone provided, fall through to next option
            pass
    
    # Priority 2: Use environment variable TZ if available
    env_tz = os.environ.get('TZ')
    if env_tz:
        try:
            # Validate the timezone from environment
            ZoneInfo(env_tz)
            return env_tz
        except Exception:
            # Invalid timezone in environment, fall through to next option
            pass
    
    # Priority 3: Extract from trip destinations
    try:
        if trip.get("destinations") and len(trip["destinations"]) > 0:
            timezone = trip["destinations"][0].get("timezone")
            if timezone:
                # Validate the timezone from trip data
                try:
                    ZoneInfo(timezone)
                    return timezone
                except Exception:
                    # Invalid timezone in trip data, fall through to fallback
                    pass
    except (IndexError, KeyError, TypeError):
        # Issue with trip data structure, fall through to fallback
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
        
        # For timestamps with Z, they're UTC
        if start_str.endswith("Z"):
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        else:
            # For timestamps without Z, assume they're Eastern Time
            from zoneinfo import ZoneInfo
            et_tz = ZoneInfo("America/New_York")
            start = datetime.fromisoformat(start_str).replace(tzinfo=et_tz)
        
        # Same handling for end date
        if end_str.endswith("Z"):
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        else:
            from zoneinfo import ZoneInfo
            et_tz = ZoneInfo("America/New_York")
            end = datetime.fromisoformat(end_str).replace(tzinfo=et_tz)
            
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


def get_common_timezones():
    """
    Return a list of common timezones for UI display.
    
    Returns:
        list: List of common timezone strings
    """
    # List of common timezones for UI dropdown
    common_timezones = [
        "UTC",
        "America/New_York",
        "America/Chicago", 
        "America/Denver",
        "America/Los_Angeles",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Asia/Tokyo",
        "Asia/Singapore",
        "Australia/Sydney",
        "Pacific/Auckland"
    ]
    
    # Ensure all timezones in the list are valid
    valid_timezones = []
    
    for tz in common_timezones:
        try:
            # Validate by attempting to create a ZoneInfo object
            ZoneInfo(tz)
            valid_timezones.append(tz)
        except Exception:
            # Skip invalid timezones
            pass
    
    return valid_timezones