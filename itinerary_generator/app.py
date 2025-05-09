from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tempfile
import sys
import logging
import traceback

# Import our main generator function instead of using CLI simulation
from itinerary_generator.generate_itinerary import generate_itinerary

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        trip_file = request.files.get('trip_json')
        template_file = request.files.get('template_html')
        generate_pdf = request.form.get('generate_pdf') == 'on'

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
            template_path = os.path.abspath("default-template.html")

        output_html = os.path.join(app.config['UPLOAD_FOLDER'], 'output.html')
        output_pdf = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf') if generate_pdf else None
        gotenberg_url = 'http://gotenberg:3000/forms/chromium/convert/html' if generate_pdf else None

        try:
            # Use the refactored generate_itinerary function directly
            html_path, pdf_path = generate_itinerary(
                json_path=trip_path,
                template_path=template_path,
                output_html=output_html,
                pdf_path=output_pdf,
                gotenberg_url=gotenberg_url
            )
            
            # Return the appropriate file
            return send_file(pdf_path if generate_pdf else html_path, as_attachment=True)
        except Exception:
            logging.error("Itinerary generation failed:\n%s", traceback.format_exc())
            return "An internal error occurred while generating the itinerary.", 500

    return render_template('form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)