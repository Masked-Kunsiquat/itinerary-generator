"""
Formatting module for handling timezones, emoji mapping, and content formatting.
"""
from datetime import datetime
from itinerary_generator.time_utils import format_time, convert_to_timezone

def insert_event(days, event_datetime, tz, label):
    """
    Insert an event into the appropriate day at the correct time.
    
    Args:
        days (list): List of day dictionaries
        event_datetime (datetime): Event time (UTC or local)
        tz (ZoneInfo): Target timezone for display
        label (str): Event label/description
    """
    # Ensure datetime is timezone-aware
    if event_datetime.tzinfo is None:
        # If it's not timezone-aware, assume it's Eastern Time
        from zoneinfo import ZoneInfo
        et_tz = ZoneInfo("America/New_York")
        event_datetime = event_datetime.replace(tzinfo=et_tz)
    
    # Convert to the local timezone for proper day allocation
    local_datetime = convert_to_timezone(event_datetime, tz)
    local_date = local_datetime.date()
    
    for day in days:
        if day["date"].date() == local_date:
            # Store the local time for display, not UTC time
            day["events"].append((local_datetime.time(), label))
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
        name = lodging["name"]

        # Parse the ISO timestamps to datetime objects
        # Handle both with and without timezone info
        try:
            # If startDate ends with Z, it was originally in UTC
            if lodging["startDate"].endswith("Z"):
                checkin = datetime.fromisoformat(lodging["startDate"].replace("Z", "+00:00"))
            else:
                # No Z suffix, assume it's Eastern Time
                from zoneinfo import ZoneInfo
                et_tz = ZoneInfo("America/New_York")
                checkin = datetime.fromisoformat(lodging["startDate"]).replace(tzinfo=et_tz)
                
            # If endDate ends with Z, it was originally in UTC
            if lodging["endDate"].endswith("Z"):
                checkout = datetime.fromisoformat(lodging["endDate"].replace("Z", "+00:00"))
            else:
                # No Z suffix, assume it's Eastern Time
                from zoneinfo import ZoneInfo
                et_tz = ZoneInfo("America/New_York")
                checkout = datetime.fromisoformat(lodging["endDate"]).replace(tzinfo=et_tz)
        except (ValueError, KeyError):
            # If there's any issue with parsing, just skip this lodging
            continue

        # Convert to local time for display
        checkin_local = convert_to_timezone(checkin, tz)
        checkout_local = convert_to_timezone(checkout, tz)
        
        # Format times for display
        checkin_time = format_time(checkin_local)
        checkout_time = format_time(checkout_local)
        
        # Add check-in and check-out events using the original UTC times
        # The insert_event function will convert them to local time
        insert_event(days, checkin, tz, f"🛏 {checkin_time} — Check-In at {name}")
        insert_event(days, checkout, tz, f"🛏 {checkout_time} — Check-Out from {name}")

        # Add lodging banners for nights at this lodging
        # Convert to local dates for comparison
        checkin_date = checkin_local.date()
        checkout_date = checkout_local.date()
        
        for day in days:
            day_date = day["date"].date()
            if checkin_date <= day_date < checkout_date:
                day["lodging_banner"] = f"🏨 Lodging: Staying at {name}"


def get_transport_description(transport):
    """
    Create a human-readable description for a transportation event.
    
    Args:
        transport (dict): Transportation data
        
    Returns:
        str: Readable description of the transportation
    """
    transport_type = transport["type"].lower()
    origin = transport["origin"]
    destination = transport["destination"]
    
    # Get provider information - handle both string and object formats
    metadata = transport.get("metadata", {})
    provider_data = metadata.get("provider", "")
    
    # Handle complex provider object
    if isinstance(provider_data, dict):
        # Use the provider name if available, otherwise the code
        provider = provider_data.get("name") or provider_data.get("code") or ""
    else:
        # Simple string provider
        provider = provider_data
    
    # Get confirmation code from either top-level or metadata
    confirmation = transport.get("confirmationCode", "")
    if not confirmation and metadata:
        confirmation = metadata.get("reservation", "")
    
    # Format based on transport type
    if transport_type == "flight":
        description = f"Flight from {origin} to {destination}"
        if provider:
            description += f" via {provider}"
    
    elif transport_type == "train":
        description = f"Train from {origin} to {destination}"
        if provider:
            description += f" ({provider})"
    
    elif transport_type == "bus":
        description = f"Bus from {origin} to {destination}"
        if provider:
            description += f" with {provider}"
    
    elif transport_type == "ferry":
        description = f"Ferry from {origin} to {destination}"
        if provider:
            description += f" with {provider}"
    
    elif transport_type == "car" and provider and provider.lower() == "rental":
        description = f"Drive rental car from {origin} to {destination}"
    
    elif transport_type == "car" and provider and provider.lower() == "self":
        description = f"Drive from {origin} to {destination}"
    
    elif transport_type == "car" and provider and provider.lower() in ["uber", "lyft", "taxi"]:
        description = f"{provider.title()} from {origin} to {destination}"
    
    else:
        # Default format
        description = f"{transport_type.title()} from {origin} to {destination}"
        if provider and provider.lower() != "self":
            description += f" with {provider}"
    
    # Add confirmation code if available
    if confirmation:
        description += f" (#{confirmation})"
    
    return description

def format_transport_events(days, transportations, tz):
    """
    Format and insert transportation events.
    
    Args:
        days (list): List of day dictionaries
        transportations (list): List of transportation dictionaries from trip data
        tz (ZoneInfo): Target timezone for display
    """
    for transport in transportations:
        # Parse the ISO timestamps to datetime objects with timezone info
        try:
            # Handle departure time
            if "departure" in transport:
                if transport["departure"].endswith("Z"):
                    departure = datetime.fromisoformat(transport["departure"].replace("Z", "+00:00"))
                else:
                    # No Z suffix, assume it's Eastern Time
                    from zoneinfo import ZoneInfo
                    et_tz = ZoneInfo("America/New_York")
                    departure = datetime.fromisoformat(transport["departure"]).replace(tzinfo=et_tz)
            else:
                continue  # Skip if no departure time
                
            # Handle arrival time
            if "arrival" in transport:
                if transport["arrival"].endswith("Z"):
                    arrival = datetime.fromisoformat(transport["arrival"].replace("Z", "+00:00"))
                else:
                    # No Z suffix, assume it's Eastern Time
                    from zoneinfo import ZoneInfo
                    et_tz = ZoneInfo("America/New_York")
                    arrival = datetime.fromisoformat(transport["arrival"]).replace(tzinfo=et_tz)
            else:
                arrival = None  # Allow for one-way trips
        except (ValueError, KeyError):
            # If there's any issue with parsing, just skip this transport
            continue
        
        # Convert to local time for display
        dep_local = convert_to_timezone(departure, tz)
        arr_local = None if arrival is None else convert_to_timezone(arrival, tz)
        
        # Get the icon for this transport type
        icon = get_transport_icon(transport["type"])
        
        # Get human-readable description
        description = get_transport_description(transport)
        
        # Add arrival info for flights and trains, or multi-day travel
        extra = ""
        if arr_local and (dep_local.date() != arr_local.date() or transport["type"] in ["flight", "train"]):
            # Format arrival time in local time
            arr_time = format_time(arr_local)
            # If different day, include the date too
            if dep_local.date() != arr_local.date():
                arr_date = arr_local.strftime('%b %-d')
                extra = f" (arrives {arr_time}, {arr_date})"  # Removed "— local time"
            else:
                extra = f" (arrives {arr_time})"  # Removed "— local time"
        
        # Format departure time in local time
        dep_time = format_time(dep_local)
        
        # Create the full label with icon, time, and description
        label = f"{icon} {dep_time} — {description}{extra}"
        
        # Insert the event
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
            
        try:
            # Parse the ISO timestamp with timezone info
            if activity["startDate"].endswith("Z"):
                start_time = datetime.fromisoformat(activity["startDate"].replace("Z", "+00:00"))
            else:
                # No Z suffix, assume it's Eastern Time
                from zoneinfo import ZoneInfo
                et_tz = ZoneInfo("America/New_York")
                start_time = datetime.fromisoformat(activity["startDate"]).replace(tzinfo=et_tz)
        except ValueError:
            # If there's any issue with parsing, just skip this activity
            continue
            
        name = activity.get("name", "Unnamed Activity")
        address = activity.get("address", "")
        
        icon = "🎟️"
        
        # Convert to local time for display
        local_datetime = convert_to_timezone(start_time, tz)
        local_time_str = format_time(local_datetime)
        
        label = f"{icon} {local_time_str} — {name}"
        
        if address and address.lower() != "n/a" and address.strip():
            label += f" @ {address}"
            
        # Insert the event using original time
        # The insert_event function will handle timezone conversion
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