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
        
        # Add check-in and check-out events
        insert_event(days, checkin, tz, f"🛏 {checkin_local.strftime('%-I:%M %p')} — Check-In at {name}")
        insert_event(days, checkout, tz, f"🛏 {checkout_local.strftime('%-I:%M %p')} — Check-Out from {name}")

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
            extra = f"(arrives {arr_local.strftime('%-I:%M %p, %b %d')} — local time)"
            
        label = f"{icon} {dep_local.strftime('%-I:%M %p')} — {transport['type'].title()} from {transport['origin']} to {transport['destination']} {extra}"
        
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
        label = f"{icon} {start_time.astimezone(tz).strftime('%-I:%M %p')} — {name}"
        
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