#!/usr/bin/env python3
"""
Itinerary Generator for Surmai trip exports.

This script serves as the main orchestrator for generating HTML and PDF itineraries
from Surmai trip.json exports using custom Jinja2 templates.
"""
import argparse
import os
import logging
import copy
from zoneinfo import ZoneInfo

# Import our modularized components
from itinerary_generator.parser import load_trip_data, get_trip_timezone, parse_dates, build_days, get_common_timezones
from itinerary_generator.formatting import populate_days
from itinerary_generator.lookups import enrich_trip_data
from itinerary_generator.renderer import create_template_context, render_itinerary, convert_to_pdf
from itinerary_generator.time_utils import get_user_timezone, get_timezone_display_info

def adjust_incorrect_utc_timestamps(trip_data):
    """Simply remove the Z suffix from all timestamps and return times as originally entered."""
    import copy
    fixed_data = copy.deepcopy(trip_data)
    
    # Process all transportation events
    for transport in fixed_data.get("transportations", []):
        # Simply remove Z suffix to keep the time as entered
        if "departure" in transport and transport["departure"].endswith("Z"):
            transport["departure"] = transport["departure"].rstrip("Z")
            
        if "arrival" in transport and transport["arrival"].endswith("Z"):
            transport["arrival"] = transport["arrival"].rstrip("Z")
    
    # Process all lodging events
    for lodging in fixed_data.get("lodgings", []):
        if "startDate" in lodging and lodging["startDate"].endswith("Z"):
            lodging["startDate"] = lodging["startDate"].rstrip("Z")
            
        if "endDate" in lodging and lodging["endDate"].endswith("Z"):
            lodging["endDate"] = lodging["endDate"].rstrip("Z")
    
    # Process all activities
    for activity in fixed_data.get("activities", []):
        if "startDate" in activity and activity["startDate"].endswith("Z"):
            activity["startDate"] = activity["startDate"].rstrip("Z")
    
    # Trip start/end dates
    if "trip" in fixed_data:
        trip = fixed_data["trip"]
        if "startDate" in trip and trip["startDate"].endswith("Z"):
            trip["startDate"] = trip["startDate"].rstrip("Z")
            
        if "endDate" in trip and trip["endDate"].endswith("Z"):
            trip["endDate"] = trip["endDate"].rstrip("Z")
    
    return fixed_data


def generate_itinerary(json_path, template_path, output_html, pdf_path=None, gotenberg_url=None, user_timezone=None):
    """
    Generate an itinerary from a Surmai trip.json file.
    
    Args:
        json_path (str): Path to the input trip.json file
        template_path (str): Path to the Jinja2 template file
        output_html (str): Path to save the rendered HTML output
        pdf_path (str, optional): Path to save PDF output (requires Gotenberg)
        gotenberg_url (str, optional): URL for Gotenberg PDF conversion service
        user_timezone (str, optional): User-specified timezone to use for display
        
    Returns:
        tuple: (html_path, pdf_path) - Paths to the generated files (pdf_path may be None)
        
    Raises:
        FileNotFoundError: If input files cannot be found
        ValueError: If there are issues with the input data format
        RuntimeError: If there are template rendering issues
    """
    try:
        # Load and parse the trip data
        trip_data = load_trip_data(json_path)
        
        # IMPORTANT: Fix the incorrectly UTC-marked timestamps
        # This adjusts for Surmai's export issue where times are in ET but marked as UTC
        trip_data = adjust_incorrect_utc_timestamps(trip_data)
        
        # Optionally enrich data (placeholder for future expansion)
        trip_data = enrich_trip_data(trip_data)
        
        # Extract key trip information
        trip = trip_data["trip"]
        start_date, end_date = parse_dates(trip)
        
        # Get the destination timezone from trip data
        dest_timezone_str = get_trip_timezone(trip)
        
        # For travel itineraries, the default should usually be the destination's timezone
        # unless the user explicitly requests a different timezone
        display_timezone_str = user_timezone or dest_timezone_str
        
        # Create timezone objects
        tz = ZoneInfo(display_timezone_str)
        dest_tz = ZoneInfo(dest_timezone_str)
        
        # Build day structures
        days = build_days(start_date, end_date)
        
        # Populate days with events
        populate_days(days, trip_data, tz)
        
        # Create template context
        context = create_template_context(trip_data, days)
        
        # Add timezone info to the context for display
        context["timezone"] = display_timezone_str
        
        # Add timezone difference info if destination timezone differs from display timezone
        if dest_timezone_str != display_timezone_str:
            context["timezone_info"] = get_timezone_display_info(display_timezone_str, dest_timezone_str)
        
        # Render HTML
        html_path = render_itinerary(template_path, context, output_html)
        
        # Optionally convert to PDF if requested
        if pdf_path:
            gotenberg_endpoint = gotenberg_url or "http://localhost:3000/forms/chromium/convert/html"
            try:
                pdf_path = convert_to_pdf(html_path, pdf_path, gotenberg_endpoint)
                return html_path, pdf_path
            except Exception as e:
                import logging
                logging.warning(f"PDF conversion failed: {e}. HTML output is still available.")
                return html_path, None
        
        return html_path, None
        
    except FileNotFoundError as e:
        # Re-raise with more context
        raise FileNotFoundError(f"Failed to generate itinerary: {e}") from e
    except KeyError as e:
        # Handle missing keys in trip data
        raise ValueError(f"Invalid trip data structure, missing key: {e}") from e
    except Exception as e:
        # Catch-all for other errors
        raise RuntimeError(f"Unexpected error generating itinerary: {e}") from e


def main():
    """
    CLI entry point for the itinerary generator.
    """
    parser = argparse.ArgumentParser(description="Render Surmai trip JSON to HTML (and optionally PDF)")
    parser.add_argument("json_path", help="Path to trip.json")
    parser.add_argument("template_path", help="Path to Jinja2 HTML template")
    parser.add_argument("output_html", help="Path to save the rendered HTML file")
    parser.add_argument("--pdf", help="If provided, path to save a PDF output via Gotenberg")
    parser.add_argument(
        "--gotenberg-url", 
        default="http://localhost:3000/forms/chromium/convert/html", 
        help="Gotenberg HTML conversion endpoint"
    )
    parser.add_argument(
        "--timezone",
        help="Timezone to use for displaying times (e.g., America/New_York, Europe/London)"
    )
    
    args = parser.parse_args()
    
    html_path, pdf_path = generate_itinerary(
        json_path=args.json_path,
        template_path=args.template_path,
        output_html=args.output_html,
        pdf_path=args.pdf,
        gotenberg_url=args.gotenberg_url,
        user_timezone=args.timezone
    )
    
    print(f"HTML itinerary generated: {html_path}")
    if pdf_path:
        print(f"PDF itinerary generated: {pdf_path}")


if __name__ == "__main__":
    main()