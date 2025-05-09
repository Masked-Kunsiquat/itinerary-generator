from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import argparse
import requests
import json
import os

def load_trip_data(path):
    with open(path, "r") as f:
        return json.load(f)

def get_trip_timezone(trip):
    return trip["destinations"][0].get("timezone", "UTC") if trip["destinations"] else "UTC"

def parse_dates(trip):
    start = datetime.fromisoformat(trip["startDate"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(trip["endDate"].replace("Z", "+00:00"))
    return start, end

def build_days(start_date, end_date):
    days = []
    for i in range((end_date - start_date).days + 1):
        current = start_date + timedelta(days=i)
        days.append({
            "date": current,
            "events": [],
            "lodging_banner": None
        })
    return days

def insert_event(days, event_datetime, tz, label):
    local_date = event_datetime.astimezone(tz).date()
    for day in days:
        if day["date"].date() == local_date:
            day["events"].append((event_datetime.astimezone(tz).time(), label))
            break

def populate_days(days, data, tz):
    for lodging in data.get("lodgings", []):
        checkin = datetime.fromisoformat(lodging["startDate"].replace("Z", "+00:00"))
        checkout = datetime.fromisoformat(lodging["endDate"].replace("Z", "+00:00"))
        name = lodging["name"]

        checkin_local = checkin.astimezone(tz)
        checkout_local = checkout.astimezone(tz)
        insert_event(days, checkin, tz, f"🛏 {checkin_local.strftime('%-I:%M %p')} — Check-In at {name}")
        insert_event(days, checkout, tz, f"🛏 {checkout_local.strftime('%-I:%M %p')} — Check-Out from {name}")


        for day in days:
            if checkin.date() < day["date"].date() < checkout.date():
                day["lodging_banner"] = f"🏨 Lodging: Staying at {name}"

    for transport in data.get("transportations", []):
        departure = datetime.fromisoformat(transport["departure"].replace("Z", "+00:00"))
        arrival = datetime.fromisoformat(transport["arrival"].replace("Z", "+00:00"))
        dep_local = departure.astimezone(tz)
        arr_local = arrival.astimezone(tz)
        icon = "✈️" if transport["type"] == "flight" else "🚗"
        extra = f"(arrives {arr_local.strftime('%-I:%M %p, %b %d')} — local time)" if departure.date() != arrival.date() else ""
        label = f"{icon} {dep_local.strftime('%-I:%M %p')} — {transport['type'].title()} from {transport['origin']} to {transport['destination']} {extra}"
        insert_event(days, departure, tz, label)

    for activity in data.get("activities", []):
        if not activity or not activity.get("startDate"):
            continue  # skip if malformed

        start_time = datetime.fromisoformat(activity["startDate"].replace("Z", "+00:00"))
        name = activity.get("name", "Unnamed Activity")
        address = activity.get("address", "")
        icon = "🎟️"
        label = f"{icon} {start_time.astimezone(tz).strftime('%-I:%M %p')} — {name}"
        if address and address.lower() != "n/a":
            label += f" @ {address}"
        insert_event(days, start_time, tz, label)


    for day in days:
        day["events"].sort(key=lambda e: e[0])

def render_itinerary(template_path, context, output_path):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)), autoescape=select_autoescape())
    template = env.get_template(os.path.basename(template_path))
    rendered = template.render(context)
    with open(output_path, "w") as f:
        f.write(rendered)
    return output_path

def convert_to_pdf(html_path, pdf_path, gotenberg_url):
    with open(html_path, 'rb') as html_file:
        files = {
            'files': ('index.html', html_file, 'text/html'),
        }
        data = {
            'landscape': 'false',
            'printBackground': 'true'
        }
        response = requests.post(gotenberg_url, files=files, data=data)
        response.raise_for_status()
        with open(pdf_path, 'wb') as f:
            f.write(response.content)

def generate_itinerary(json_path, template_path, output_html, pdf_path=None, gotenberg_url=None):
    trip_data = load_trip_data(json_path)
    trip = trip_data["trip"]
    start_date, end_date = parse_dates(trip)
    tz = ZoneInfo(get_trip_timezone(trip))
    days = build_days(start_date, end_date)
    populate_days(days, trip_data, tz)

    context = {
        "trip_name": trip["name"],
        "start_date": start_date.strftime("%b %d, %Y"),
        "end_date": end_date.strftime("%b %d, %Y"),
        "days": days,
        "trip_notes": trip.get("notes", ""),
        "lodgings": trip_data.get("lodgings", []),
        "transportations": trip_data.get("transportations", [])
    }

    html_path = render_itinerary(template_path, context, output_html)

    if pdf_path:
        convert_to_pdf(html_path, pdf_path, gotenberg_url or "http://localhost:3000/forms/chromium/convert/html")

def main():
    parser = argparse.ArgumentParser(description="Render Surmai trip JSON to HTML (and optionally PDF)")
    parser.add_argument("json_path", help="Path to trip.json")
    parser.add_argument("template_path", help="Path to Jinja2 HTML template")
    parser.add_argument("output_html", help="Path to save the rendered HTML file")
    parser.add_argument("--pdf", help="If provided, path to save a PDF output via Gotenberg")
    parser.add_argument("--gotenberg-url", default="http://localhost:3000/forms/chromium/convert/html", help="Gotenberg HTML conversion endpoint")
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