# itinerary_generator/formatting.py
"""
Formatting module for handling timezones, emoji mapping, and content formatting.
"""
from datetime import datetime
from zoneinfo import ZoneInfo # Ensure this is at the module level
from itinerary_generator.time_utils import format_time, convert_to_timezone

def insert_event(days, event_datetime, tz, label):
    """
    Insert an event into the appropriate day at the correct time.
    
    Args:
        days (list): List of day dictionaries
        event_datetime (datetime): Event time (UTC or local). If naive, assumed to be Eastern Time.
        tz (ZoneInfo): Target timezone for display
        label (str): Event label/description
    """
    # Ensure datetime is timezone-aware
    if event_datetime.tzinfo is None:
        et_tz = ZoneInfo("America/New_York") 
        event_datetime = event_datetime.replace(tzinfo=et_tz)
    
    local_datetime = convert_to_timezone(event_datetime, tz)
    local_date = local_datetime.date()
    
    for day in days:
        if day["date"].date() == local_date:
            day["events"].append((local_datetime.time(), label))
            break

def get_transport_icon(transport_type):
    """
    Map transport types to emoji icons.
    """
    icons = {
        "flight": "✈️", "train": "🚆", "bus": "🚌", "ferry": "⛴️",
        "car": "🚗", "taxi": "🚕", "rideshare": "🚙", "subway": "🚇",
        "bike": "🚲", "walk": "🚶",
    }
    return icons.get(str(transport_type).lower(), "🚗")


def format_lodging_events(days, lodgings, tz):
    """
    Format and insert lodging check-in/out events and day banners.
    """
    for lodging in lodgings:
        try:
            name = lodging["name"]
            start_date_str = lodging.get("startDate")
            end_date_str = lodging.get("endDate")

            if not start_date_str or not end_date_str:
                continue 

            if start_date_str.endswith("Z"):
                checkin = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            else:
                et_tz = ZoneInfo("America/New_York")
                checkin = datetime.fromisoformat(start_date_str).replace(tzinfo=et_tz)
                
            if end_date_str.endswith("Z"):
                checkout = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            else:
                et_tz = ZoneInfo("America/New_York")
                checkout = datetime.fromisoformat(end_date_str).replace(tzinfo=et_tz)
        except (ValueError, KeyError): # Catch issues if name is missing or dates are malformed
            continue

        checkin_local = convert_to_timezone(checkin, tz)
        checkout_local = convert_to_timezone(checkout, tz)
        
        checkin_time_str = format_time(checkin_local)
        checkout_time_str = format_time(checkout_local)
        
        insert_event(days, checkin, tz, f"🛏 {checkin_time_str} — Check-In at {name}")
        insert_event(days, checkout, tz, f"🛏 {checkout_time_str} — Check-Out from {name}")

        checkin_date = checkin_local.date()
        checkout_date = checkout_local.date()
        
        for day in days:
            day_date = day["date"].date()
            if checkin_date <= day_date < checkout_date:
                day["lodging_banner"] = f"🏨 Lodging: Staying at {name}"


def get_transport_description(transport):
    """
    Create a human-readable description for a transportation event.
    """
    transport_type = str(transport.get("type", "unknown")).lower()
    origin = transport.get("origin", "Unknown Origin")
    destination = transport.get("destination", "Unknown Destination")
    
    metadata = transport.get("metadata", {})
    provider_data = metadata.get("provider", "")
    
    provider = ""
    if isinstance(provider_data, dict):
        provider = provider_data.get("name") or provider_data.get("code") or ""
    elif isinstance(provider_data, str):
        provider = provider_data
    
    confirmation = transport.get("confirmationCode") or metadata.get("reservation", "")
    
    description_parts = []

    if transport_type == "flight":
        description_parts.append(f"Flight from {origin} to {destination}")
        if provider:
            description_parts.append(f"via {provider}")
    elif transport_type == "train":
        description_parts.append(f"Train from {origin} to {destination}")
        if provider:
            description_parts.append(f"({provider})")
    elif transport_type == "bus":
        description_parts.append(f"Bus from {origin} to {destination}")
        if provider:
            description_parts.append(f"with {provider}")
    elif transport_type == "ferry":
        description_parts.append(f"Ferry from {origin} to {destination}")
        if provider:
            description_parts.append(f"with {provider}")
    elif transport_type == "car":
        provider_lower = provider.lower()
        if provider_lower == "rental":
            description_parts.append(f"Drive rental car from {origin} to {destination}")
        elif provider_lower == "self":
            description_parts.append(f"Drive from {origin} to {destination}")
        elif provider_lower in ["uber", "lyft", "taxi"]:
            description_parts.append(f"{provider.title()} from {origin} to {destination}")
        else: 
            description_parts.append(f"Car from {origin} to {destination}")
            if provider: 
                 description_parts.append(f"with {provider}")
    else: 
        description_parts.append(f"{transport_type.title()} from {origin} to {destination}")
        if provider and provider.lower() != "self": # Avoid "with Self"
            description_parts.append(f"with {provider}")
    
    description = " ".join(filter(None, description_parts))

    if confirmation:
        description += f" (#{confirmation})"
    
    return description

def format_transport_events(days, transportations, tz):
    """
    Format and insert transportation events.
    """
    for transport in transportations:
        try:
            departure_str = transport.get("departure")
            arrival_str = transport.get("arrival")

            if not departure_str:
                continue 
                
            if departure_str.endswith("Z"):
                departure = datetime.fromisoformat(departure_str.replace("Z", "+00:00"))
            else:
                et_tz = ZoneInfo("America/New_York")
                departure = datetime.fromisoformat(departure_str).replace(tzinfo=et_tz)
            
            arrival = None
            if arrival_str: # Only parse if arrival_str has a value
                if arrival_str.endswith("Z"):
                    arrival = datetime.fromisoformat(arrival_str.replace("Z", "+00:00"))
                else:
                    et_tz = ZoneInfo("America/New_York")
                    arrival = datetime.fromisoformat(arrival_str).replace(tzinfo=et_tz)
        except (ValueError, KeyError): 
            continue
        
        dep_local = convert_to_timezone(departure, tz)
        arr_local = None if arrival is None else convert_to_timezone(arrival, tz)
        
        icon = get_transport_icon(transport.get("type", "unknown"))
        description = get_transport_description(transport)
        
        extra_info = ""
        # Ensure arr_local is not None before trying to access its properties
        if arr_local and (dep_local.date() != arr_local.date() or transport.get("type", "").lower() in ["flight", "train"]):
            arr_time_str = format_time(arr_local)
            if dep_local.date() != arr_local.date():
                arr_date_str = arr_local.strftime('%b %-d')
                extra_info = f" (arrives {arr_time_str}, {arr_date_str})"
            else:
                extra_info = f" (arrives {arr_time_str})"
        
        dep_time_str = format_time(dep_local)
        label = f"{icon} {dep_time_str} — {description}{extra_info}"
        
        insert_event(days, departure, tz, label)
        

def format_activity_events(days, activities, tz):
    """
    Format and insert activity events.
    """
    for activity in activities:
        start_date_str = activity.get("startDate")
        if not start_date_str:
            continue
            
        try:
            if start_date_str.endswith("Z"):
                start_time = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            else:
                et_tz = ZoneInfo("America/New_York")
                start_time = datetime.fromisoformat(start_date_str).replace(tzinfo=et_tz)
        except ValueError: 
            continue
            
        name = activity.get("name", "Unnamed Activity")
        address = activity.get("address", "") # Default to empty string
        icon = "🎟️"
        
        local_datetime = convert_to_timezone(start_time, tz)
        local_time_str = format_time(local_datetime)
        
        label = f"{icon} {local_time_str} — {name}"
        
        # Ensure address is a string before calling strip() and lower()
        if address and isinstance(address, str) and address.strip().lower() not in ["", "n/a"]:
            label += f" @ {address}"
            
        insert_event(days, start_time, tz, label)


def populate_days(days, data, tz):
    """
    Populate days with all events from trip data.
    """
    format_lodging_events(days, data.get("lodgings", []), tz)
    format_transport_events(days, data.get("transportations", []), tz)
    format_activity_events(days, data.get("activities", []), tz)
    
    for day in days:
        day["events"].sort(key=lambda e: e[0])