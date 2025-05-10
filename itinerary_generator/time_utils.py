"""
Time utilities for timezone handling and date/time formatting.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
import os


def get_user_timezone(user_timezone=None):
    """
    Get the most appropriate timezone based on user preference or environment.
    
    Priority:
    1. User-provided timezone (if valid)
    2. Environment variable TZ
    3. UTC fallback
    
    Args:
        user_timezone (str, optional): User-specified timezone
        
    Returns:
        ZoneInfo: Timezone object for the selected timezone
    """
    # Priority 1: Use user-provided timezone if valid
    if user_timezone:
        try:
            return ZoneInfo(user_timezone)
        except Exception:
            pass
    
    # Priority 2: Use environment variable TZ if available
    env_tz = os.environ.get('TZ')
    if env_tz:
        try:
            return ZoneInfo(env_tz)
        except Exception:
            pass
    
    # Priority 3: Fallback to UTC
    return ZoneInfo("UTC")


def format_date(date, format_str="%b %d, %Y"):
    """
    Format a datetime in a consistent way.
    
    Args:
        date (datetime): Datetime object to format
        format_str (str, optional): Format string
        
    Returns:
        str: Formatted date string
    """
    return date.strftime(format_str)


def format_time(dt, include_ampm=True):
    """
    Format a datetime in a consistent way with no leading zeros.
    
    Args:
        dt (datetime): Datetime object to format
        include_ampm (bool, optional): Whether to include AM/PM
        
    Returns:
        str: Formatted time string (e.g., "9:30 AM" instead of "09:30 AM")
    """
    if include_ampm:
        return dt.strftime('%-I:%M %p')
    return dt.strftime('%-H:%M')


def convert_to_timezone(dt, timezone):
    """
    Convert a datetime to another timezone.
    
    Args:
        dt (datetime): Datetime object to convert (must be timezone-aware)
        timezone (str or ZoneInfo): Target timezone
        
    Returns:
        datetime: Datetime in the target timezone
    """
    if isinstance(timezone, str):
        timezone = ZoneInfo(timezone)
    
    # Ensure datetime is timezone-aware
    if dt.tzinfo is None:
        raise ValueError("Input datetime must be timezone-aware")
    
    return dt.astimezone(timezone)


def calculate_timezone_difference(source_tz, target_tz):
    """
    Calculate the hour difference between two timezones.
    
    Args:
        source_tz (str or ZoneInfo): Source timezone
        target_tz (str or ZoneInfo): Target timezone
        
    Returns:
        float: Hour difference (positive if target is ahead, negative if behind)
    """
    # Convert string timezones to ZoneInfo if needed
    if isinstance(source_tz, str):
        source_tz = ZoneInfo(source_tz)
    if isinstance(target_tz, str):
        target_tz = ZoneInfo(target_tz)
    
    # Use current datetime for the calculation
    now = datetime.now(ZoneInfo("UTC"))
    time_source = now.astimezone(source_tz)
    time_target = now.astimezone(target_tz)
    
    # Calculate offset difference in hours
    offset_source = time_source.utcoffset().total_seconds() / 3600
    offset_target = time_target.utcoffset().total_seconds() / 3600
    
    return offset_target - offset_source


def get_timezone_display_info(user_timezone, destination_timezone):
    """
    Get user-friendly timezone difference information.
    
    Args:
        user_timezone (str or ZoneInfo): User's timezone
        destination_timezone (str or ZoneInfo): Destination timezone
        
    Returns:
        dict: Dictionary with timezone info including difference
    """
    # Calculate the difference
    diff = calculate_timezone_difference(user_timezone, destination_timezone)
    
    # Generate a user-friendly message
    if diff == 0:
        message = "There is no time difference between your timezone and the destination."
    elif diff > 0:
        message = f"The destination is {abs(diff)} hours ahead of your timezone."
    else:
        message = f"The destination is {abs(diff)} hours behind your timezone."
    
    # Return structured information
    return {
        "difference": diff,
        "message": message,
        "user_timezone": user_timezone if isinstance(user_timezone, str) else str(user_timezone),
        "destination_timezone": destination_timezone if isinstance(destination_timezone, str) else str(destination_timezone)
    }