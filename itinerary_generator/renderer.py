"""
Renderer module for Jinja2 template rendering and Gotenberg PDF conversion.
"""
import os
import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape


def create_template_context(trip_data, days):
    """
    Create the template context with all necessary variables.
    
    Args:
        trip_data (dict): Processed trip data
        days (list): List of day dictionaries with events
        
    Returns:
        dict: Template context dictionary with all variables needed by templates
    """
    trip = trip_data["trip"]
    start_date = days[0]["date"] if days else None
    end_date = days[-1]["date"] if days else None
    
    return {
        "trip_name": trip["name"],
        "start_date": start_date.strftime("%b %d, %Y") if start_date else "",
        "end_date": end_date.strftime("%b %d, %Y") if end_date else "",
        "days": days,
        "trip_notes": trip.get("notes", ""),
        "lodgings": trip_data.get("lodgings", []),
        "transportations": trip_data.get("transportations", [])
    }


def render_itinerary(template_path, context, output_path):
    """
    Render the itinerary using Jinja2 templates.
    
    Args:
        template_path (str): Path to the Jinja2 template file
        context (dict): Template context with variables
        output_path (str): Path where the rendered HTML should be saved
        
    Returns:
        str: Path to the rendered HTML file
    """
    # Check if the template is a full path or just a filename
    if os.path.isfile(template_path):
        # It's a full path to an existing file
        template_dir = os.path.dirname(template_path)
        template_file = os.path.basename(template_path)
    else:
        # It's just a filename, try to find it in multiple locations
        template_file = os.path.basename(template_path)
        
        # Define possible template locations to search
        possible_dirs = [
            os.path.dirname(template_path),  # Original directory
            os.path.join(os.path.dirname(__file__), 'templates'),  # Module's templates directory
            'templates',  # Templates in current directory
            '/app/templates',  # Docker container path
            '/app/itinerary_generator/templates',  # Docker container module path
        ]
        
        # Find the first directory that contains the template
        template_dir = None
        for dir_path in possible_dirs:
            if dir_path and os.path.isdir(dir_path) and os.path.isfile(os.path.join(dir_path, template_file)):
                template_dir = dir_path
                break
                
        if not template_dir:
            # If still not found, raise a more helpful error
            dirs_checked = '\n - '.join([d for d in possible_dirs if d])
            raise FileNotFoundError(
                f"Template file '{template_file}' not found. Searched in:\n - {dirs_checked}\n"
                f"Please ensure the template exists in one of these directories."
            )

    # Create Jinja2 environment with the template directory
    env = Environment(
        loader=FileSystemLoader(template_dir), 
        autoescape=select_autoescape()
    )
    
    # Load and render the template
    template = env.get_template(template_file)
    rendered = template.render(context)
    
    # Write the rendered HTML to the output file
    with open(output_path, "w") as f:
        f.write(rendered)
        
    return output_path


def convert_to_pdf(html_path, pdf_path, gotenberg_url):
    """
    Convert HTML to PDF using Gotenberg service.
    
    Args:
        html_path (str): Path to the rendered HTML file
        pdf_path (str): Path where the PDF should be saved
        gotenberg_url (str): URL of the Gotenberg service
        
    Returns:
        str: Path to the generated PDF or None if conversion failed
        
    Raises:
        requests.HTTPError: If Gotenberg returns an error status
    """
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
            
    return pdf_path