from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tempfile
from generate_itinerary import main as generate_main
import sys

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

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
        output_pdf = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')

        # Simulate CLI args for generate_itinerary.py
        sys.argv = [
            'generate_itinerary.py',
            trip_path,
            template_path,
            output_html
        ]
        if generate_pdf:
            sys.argv += ['--pdf', output_pdf, '--gotenberg-url', 'http://gotenberg:3000/forms/chromium/convert/html']

        try:
            generate_main()
            return send_file(output_pdf if generate_pdf else output_html, as_attachment=True)
        except Exception as e:
            return f"Failed to generate: {e}", 500

    return render_template('form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
