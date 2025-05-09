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
    # Create a temporary directory for all test outputs
    with tempfile.TemporaryDirectory() as temp_dir:
        html_path = os.path.join(temp_dir, "output.html")
        pdf_path = os.path.join(temp_dir, "output.pdf")
        
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
                pdf_path=pdf_path,
                gotenberg_url="http://localhost:3000/forms/chromium/convert/html"
            )
        
        # Verify the HTML file was created
        assert os.path.exists(html_result)
        
        # Check for key content in the generated HTML
        with open(html_result, 'r') as f:
            content = f.read()
            assert "Test Trip" in content
        
        # Verify PDF result
        assert os.path.exists(pdf_result)
        
        # The TemporaryDirectory will automatically clean up when exiting the context