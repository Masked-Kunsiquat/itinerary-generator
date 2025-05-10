from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tempfile
import logging
import traceback
import json

# Import our main generator function instead of using CLI simulation
from itinerary_generator.generate_itinerary import generate_itinerary
from itinerary_generator.parser import get_common_timezones, get_trip_timezone, load_trip_data

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        trip_file = request.files.get('trip_json')
        template_file = request.files.get('template_html')
        generate_pdf = request.form.get('generate_pdf') == 'on'
        user_timezone = request.form.get('timezone')
        
        if not user_timezone or user_timezone == 'auto':
            user_timezone = None  # Let the system auto-detect from trip data

        if not trip_file:
            return "Missing trip.json file", 400

        # Save trip.json
        trip_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(trip_file.filename))
        trip_file.save(trip_path)

        # Use uploaded template if provided, else fallback to default
        if template_file and template_file.filename:
            template_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(template_file.filename))
            template_file.save(template_path)
        else:
            # Check several possible locations for the default template
            possible_templates = [
                os.path.abspath("default-template.html"),
                os.path.join(os.path.dirname(__file__), "templates", "default-template.html"),
                "/app/default-template.html",
                "/app/itinerary_generator/templates/default-template.html"
            ]
            
            template_path = None
            for path in possible_templates:
                if os.path.exists(path):
                    template_path = path
                    break
                    
            if not template_path:
                return "Could not find default template. Please upload a template file.", 500

        output_html = os.path.join(app.config['UPLOAD_FOLDER'], 'output.html')
        output_pdf = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf') if generate_pdf else None
        gotenberg_url = 'http://gotenberg:3000/forms/chromium/convert/html' if generate_pdf else None

        try:
            # Use the modularized generate_itinerary function with timezone parameter
            html_path, pdf_path = generate_itinerary(
                json_path=trip_path,
                template_path=template_path,
                output_html=output_html,
                pdf_path=output_pdf,
                gotenberg_url=gotenberg_url,
                user_timezone=user_timezone
            )
            
            # Return the appropriate file
            return send_file(pdf_path if generate_pdf and pdf_path else html_path, as_attachment=True)
        except Exception:
            logging.error("Itinerary generation failed:\n%s", traceback.format_exc())
            return "An internal error occurred while generating the itinerary.", 500

    # For GET requests, try to auto-detect destination timezone from the trip
    detected_timezone = None
    
    # Get list of common timezones for the dropdown
    timezones = get_common_timezones()
    return render_template('form.html', timezones=timezones, detected_timezone=detected_timezone)

if __name__ == '__main__':
    # Use environment variable to control debug mode, default to False for security
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)