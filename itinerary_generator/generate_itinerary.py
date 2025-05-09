#!/usr/bin/env python3
"""
Itinerary Generator for Surmai trip exports.

This script serves as the main orchestrator for generating HTML and PDF itineraries
from Surmai trip.json exports using custom Jinja2 templates.
"""
import argparse
import os
from zoneinfo import ZoneInfo

# Import our modularized components
from itinerary_generator.parser import load_trip_data, get_trip_timezone, parse_dates, build_days
from itinerary_generator.formatting import populate_days
from itinerary_generator.lookups import enrich_trip_data
from itinerary_generator.renderer import create_template_context, render_itinerary, convert_to_pdf


def generate_itinerary(json_path, template_path, output_html, pdf_path=None, gotenberg_url=None):
    """
    Generate an itinerary from a Surmai trip.json file.
    
    Args:
        json_path (str): Path to the input trip.json file
        template_path (str): Path to the Jinja2 template file
        output_html (str): Path to save the rendered HTML output
        pdf_path (str, optional): Path to save PDF output (requires Gotenberg)
        gotenberg_url (str, optional): URL for Gotenberg PDF conversion service
        
    Returns:
        tuple: (html_path, pdf_path) - Paths to the generated files (pdf_path may be None)
    """
    # Load and parse the trip data
    trip_data = load_trip_data(json_path)
    
    # Optionally enrich data (placeholder for future expansion)
    trip_data = enrich_trip_data(trip_data)
    
    # Extract key trip information
    trip = trip_data["trip"]
    start_date, end_date = parse_dates(trip)
    tz = ZoneInfo(get_trip_timezone(trip))
    
    # Build day structures
    days = build_days(start_date, end_date)
    
    # Populate days with events
    populate_days(days, trip_data, tz)
    
    # Create template context
    context = create_template_context(trip_data, days)
    
    # Render HTML
    html_path = render_itinerary(template_path, context, output_html)
    
    # Optionally convert to PDF if requested
    if pdf_path:
        gotenberg_endpoint = gotenberg_url or "http://localhost:3000/forms/chromium/convert/html"
        pdf_path = convert_to_pdf(html_path, pdf_path, gotenberg_endpoint)
        return html_path, pdf_path
    
    return html_path, None


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
    
    args = parser.parse_args()
    
    generate_itinerary(
        json_path=args.json_path,
        template_path=args.template_path,
        output_html=args.output_html,
        pdf_path=args.pdf,
        gotenberg_url=args.gotenberg_url
    )


if __name__ == "__main__":
    main()