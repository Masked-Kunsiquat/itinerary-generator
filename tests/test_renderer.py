import os
import pytest
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import requests

from itinerary_generator.renderer import create_template_context, render_itinerary, convert_to_pdf


@pytest.fixture
def sample_trip_data():
    """Sample trip data for template context."""
    return {
        "trip": {
            "name": "Test Trip",
            "startDate": "2025-05-10T00:00:00Z",
            "endDate": "2025-05-15T00:00:00Z",
            "notes": "<p>Test notes</p>"
        },
        "lodgings": [
            {"name": "Test Hotel", "address": "123 Test St"}
        ],
        "transportations": [
            {"type": "flight", "origin": "A", "destination": "B"}
        ]
    }


@pytest.fixture
def sample_days():
    """Sample days for template context."""
    start = datetime.fromisoformat("2025-05-10T00:00:00+00:00")
    end = datetime.fromisoformat("2025-05-15T00:00:00+00:00")
    
    days = []
    for i in range((end - start).days + 1):
        # Use timedelta for proper date calculation across month boundaries
        current = start + timedelta(days=i)
        days.append({
            "date": current,
            "events": [(current.replace(hour=10).time(), "Test Event")],
            "lodging_banner": "Test Banner" if i > 0 else None
        })
    
    return days


def test_create_template_context(sample_trip_data, sample_days):
    """Test creating a template context with all variables."""
    context = create_template_context(sample_trip_data, sample_days)
    
    assert context["trip_name"] == "Test Trip"
    assert "May 10, 2025" in context["start_date"]
    assert "May 15, 2025" in context["end_date"]
    assert context["days"] == sample_days
    assert context["trip_notes"] == "<p>Test notes</p>"
    assert len(context["lodgings"]) == 1
    assert len(context["transportations"]) == 1


def test_create_template_context_empty_days(sample_trip_data):
    """Test creating context with empty days list."""
    context = create_template_context(sample_trip_data, [])
    
    assert context["trip_name"] == "Test Trip"
    assert context["start_date"] == ""
    assert context["end_date"] == ""
    assert context["days"] == []


def test_render_itinerary(sample_trip_data, sample_days):
    """Test rendering an itinerary to HTML."""
    # Create a simple test template
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp:
        temp.write("{{ trip_name }} - {{ days|length }} days")
        template_path = temp.name
    
    # Create secure output file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as output_file:
        output_path = output_file.name
    
    try:
        # Render the template
        context = create_template_context(sample_trip_data, sample_days)
        html_path = render_itinerary(template_path, context, output_path)
        
        # Check that the output file exists and contains rendered content
        assert os.path.exists(html_path)
        with open(html_path, 'r') as f:
            content = f.read()
            assert "Test Trip - 6 days" in content
    finally:
        # Clean up temp files
        if os.path.exists(template_path):
            os.unlink(template_path)
        if os.path.exists(output_path):
            os.unlink(output_path)

def test_render_itinerary_template_in_module_subdir(sample_trip_data, sample_days, monkeypatch):
    """Test rendering when template is in a standard 'templates' subdirectory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        module_dir = os.path.join(tmpdir, "itinerary_generator")
        templates_subdir = os.path.join(module_dir, "templates")
        os.makedirs(templates_subdir)

        template_content = "{{ trip_name }} - Found in module subdir"
        template_filename = "module_subdir_template.html"
        actual_template_path = os.path.join(templates_subdir, template_filename)
        
        with open(actual_template_path, "w") as f:
            f.write(template_content)

        output_path = os.path.join(tmpdir, "output_module_subdir.html")
        context = create_template_context(sample_trip_data, sample_days)

        # Get a reference to the original os.path.dirname
        original_dirname = os.path.dirname 

        def mock_dirname(path_arg):
            # If the path_arg is what __file__ would be for renderer.py, return our simulated module_dir
            if isinstance(path_arg, str) and path_arg.endswith('renderer.py'):
                return module_dir
            # Otherwise, call the original os.path.dirname
            return original_dirname(path_arg)

        monkeypatch.setattr('itinerary_generator.renderer.os.path.dirname', mock_dirname)
        
        html_path_result = render_itinerary(template_filename, context, output_path)

        assert os.path.exists(html_path_result)
        with open(html_path_result, 'r') as f:
            content_read = f.read()
            assert "Test Trip - Found in module subdir" in content_read

def test_render_itinerary_template_not_found(sample_trip_data, sample_days):
    """Test rendering when the template file cannot be found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "output_not_found.html")
        context = create_template_context(sample_trip_data, sample_days)
        
        non_existent_template = "this_template_does_not_exist.html"
        
        with pytest.raises(FileNotFoundError) as excinfo:
            render_itinerary(non_existent_template, context, output_path)
        
        assert f"Template file '{non_existent_template}' not found" in str(excinfo.value)
        assert "Searched in:" in str(excinfo.value) # Check for the helpful part of the message


@patch("requests.post")
def test_convert_to_pdf_success(mock_post):
    """Test successful PDF conversion with Gotenberg."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"%PDF-1.5 test data"
    mock_post.return_value = mock_response
    
    # Create a test HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp:
        temp.write("<html><body>Test</body></html>")
        html_path = temp.name
    
    # Create secure PDF output file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as pdf_file:
        pdf_path = pdf_file.name
    
    try:
        # Convert HTML to PDF
        result = convert_to_pdf(html_path, pdf_path, "http://fake-gotenberg")
        
        # Check that PDF was created and contains the expected content
        assert result == pdf_path
        assert os.path.exists(pdf_path)
        with open(pdf_path, 'rb') as f:
            content = f.read()
            assert content.startswith(b"%PDF")
        
        # Check that requests.post was called correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://fake-gotenberg"
        assert "files" in kwargs
        assert "data" in kwargs
    finally:
        # Clean up temp files
        if os.path.exists(html_path):
            os.unlink(html_path)
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)


@patch("requests.post")
def test_convert_to_pdf_error(mock_post):
    """Test error handling in PDF conversion."""
    # Mock error response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError("Gotenberg failed")
    mock_post.return_value = mock_response
    
    # Create a test HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp:
        temp.write("<html><body>Test</body></html>")
        html_path = temp.name
    
    # Create secure PDF output file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as pdf_file:
        pdf_path = pdf_file.name
    
    try:
        # Check that exception is raised
        with pytest.raises(requests.HTTPError, match="Gotenberg failed"):
            convert_to_pdf(html_path, pdf_path, "http://fake-gotenberg")
    finally:
        # Clean up temp files
        if os.path.exists(html_path):
            os.unlink(html_path)
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
