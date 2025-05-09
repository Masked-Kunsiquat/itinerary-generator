"""
Formatting module for handling timezones, emoji mapping, and content formatting.
"""
from datetime import datetime


def insert_event(days, event_datetime, tz, label):
    """
    Insert an event into the appropriate day at the correct time.
    
    Args:
        days (list): List of day dictionaries
        event_datetime (datetime): Event time (UTC)
        tz (ZoneInfo): Target timezone for display
        label (str): Event label/description
    """
    local_date = event_datetime.astimezone(tz).date()
    for day in days:
        if day["date"].date() == local_date:
            day["events"].append((event_datetime.astimezone(tz).time(), label))
            break


def get_transport_icon(transport_type):
    """
    Map transport types to emoji icons.
    
    Args:
        transport_type (str): Type of transportation
        
    Returns:
        str: Emoji icon representing the transport type
    """
    icons = {
        "flight": "✈️",
        "train": "🚆",
        "bus": "🚌",
        "ferry": "⛴️",
        "car": "🚗",
        "taxi": "🚕",
        "rideshare": "🚙",
        "subway": "🚇",
        "bike": "🚲",
        "walk": "🚶",
    }
    return icons.get(transport_type.lower(), "🚗")


def format_time(dt):
    """
    Format a datetime in a Windows-compatible way with no leading zeros.
    
    Args:
        dt (datetime): Datetime object to format
        
    Returns:
        str: Formatted time string (e.g., "9:30 AM" instead of "09:30 AM")
    """
    return dt.strftime('%I:%M %p').lstrip('0')


def format_lodging_events(days, lodgings, tz):
    """
    Format and insert lodging check-in/out events and day banners.
    
    Args:
        days (list): List of day dictionaries
        lodgings (list): List of lodging dictionaries from trip data
        tz (ZoneInfo): Target timezone for display
    """
    for lodging in lodgings:
        checkin = datetime.fromisoformat(lodging["startDate"].replace("Z", "+00:00"))
        checkout = datetime.fromisoformat(lodging["endDate"].replace("Z", "+00:00"))
        name = lodging["name"]

        checkin_local = checkin.astimezone(tz)
        checkout_local = checkout.astimezone(tz)
        
        # Format times in a Windows-compatible way
        checkin_time = format_time(checkin_local)
        checkout_time = format_time(checkout_local)
        
        # Add check-in and check-out events
        insert_event(days, checkin, tz, f"🛏 {checkin_time} — Check-In at {name}")
        insert_event(days, checkout, tz, f"🛏 {checkout_time} — Check-Out from {name}")

        # Add lodging banners for nights at this lodging
        for day in days:
            if checkin.date() <= day["date"].date() < checkout.date():
                day["lodging_banner"] = f"🏨 Lodging: Staying at {name}"


def format_transport_events(days, transportations, tz):
    """
    Format and insert transportation events.
    
    Args:
        days (list): List of day dictionaries
        transportations (list): List of transportation dictionaries from trip data
        tz (ZoneInfo): Target timezone for display
    """
    for transport in transportations:
        departure = datetime.fromisoformat(transport["departure"].replace("Z", "+00:00"))
        arrival = datetime.fromisoformat(transport["arrival"].replace("Z", "+00:00"))
        
        dep_local = departure.astimezone(tz)
        arr_local = arrival.astimezone(tz)
        
        icon = get_transport_icon(transport["type"])
        
        # Add extra info for multi-day transportation
        extra = ""
        if departure.date() != arrival.date():
            # Format arrival time in a Windows-compatible way
            arr_time = format_time(arr_local)
            arr_date = arr_local.strftime('%b %d')
            extra = f"(arrives {arr_time}, {arr_date} — local time)"
        
        # Format departure time in a Windows-compatible way
        dep_time = format_time(dep_local)
        label = f"{icon} {dep_time} — {transport['type'].title()} from {transport['origin']} to {transport['destination']} {extra}"
        
        insert_event(days, departure, tz, label)


def format_activity_events(days, activities, tz):
    """
    Format and insert activity events.
    
    Args:
        days (list): List of day dictionaries
        activities (list): List of activity dictionaries from trip data
        tz (ZoneInfo): Target timezone for display
    """
    for activity in activities:
        if not activity or not activity.get("startDate"):
            continue  # skip if malformed
            
        start_time = datetime.fromisoformat(activity["startDate"].replace("Z", "+00:00"))
        name = activity.get("name", "Unnamed Activity")
        address = activity.get("address", "")
        
        icon = "🎟️"
        
        # Format time in a Windows-compatible way
        local_time = format_time(start_time.astimezone(tz))
        label = f"{icon} {local_time} — {name}"
        
        if address and address.lower() != "n/a" and address.strip():
            label += f" @ {address}"
            
        insert_event(days, start_time, tz, label)


def populate_days(days, data, tz):
    """
    Populate days with all events from trip data.
    
    Args:
        days (list): List of day dictionaries
        data (dict): Trip data from Surmai JSON
        tz (ZoneInfo): Target timezone for display
    """
    # Add lodging events and banners
    format_lodging_events(days, data.get("lodgings", []), tz)
    
    # Add transportation events
    format_transport_events(days, data.get("transportations", []), tz)
    
    # Add activity events
    format_activity_events(days, data.get("activities", []), tz)
    
    # Sort events by time in each day
    for day in days:
        day["events"].sort(key=lambda e: e[0])