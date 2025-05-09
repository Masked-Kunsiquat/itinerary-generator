import sys
import os
import tempfile
import io
import pytest
from unittest.mock import patch, MagicMock

from itinerary_generator.generate_itinerary import generate_itinerary


@pytest.mark.integration
def test_full_generation_flow(fake_json_file, fake_template_file):
    """
    Integration test for the full itinerary generation flow.
    Tests the interaction between all modules.
    """
    # Create temporary output files
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as html_file:
        html_path = html_file.name
    
    # Mock the PDF conversion to avoid Gotenberg dependency
    with patch('requests.post') as mock_post:
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"%PDF-1.5 test content"
        mock_post.return_value = mock_response
        
        # Generate the itinerary using the sample data
        html_result, pdf_result = generate_itinerary(
            json_path=fake_json_file,
            template_path=fake_template_file,
            output_html=html_path,
            pdf_path="output.pdf",
            gotenberg_url="http://localhost:3000/forms/chromium/convert/html"
        )
    
    try:
        # Verify the HTML file was created
        assert os.path.exists(html_result)
        
        # Check for key content in the generated HTML
        with open(html_result, 'r') as f:
            content = f.read()
            assert "Test Trip" in content
    finally:
        # Clean up
        if os.path.exists(html_path):
            os.unlink(html_path)
        if os.path.exists("output.pdf"):
            os.unlink("output.pdf")