import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import requests
import tempfile

from itinerary_generator.renderer import convert_to_pdf


@patch("requests.post")
def test_convert_to_pdf_success(mock_post):
    """Test successful PDF conversion with Gotenberg."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"%PDF dummy content"
    mock_post.return_value = mock_response

    # Create input and output files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as html_file:
        html_file.write("<html><body>Test</body></html>")
        html_path = html_file.name
    
    try:
        pdf_path = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
        
        # Call the function
        result = convert_to_pdf(html_path, pdf_path, "http://fake-gotenberg")
        
        # Verify the result
        assert result == pdf_path
        assert os.path.exists(pdf_path)
        
        # Verify mock was called correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://fake-gotenberg"
        assert "files" in kwargs
        assert "data" in kwargs
    finally:
        # Clean up
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
    
    # Create test files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as html_file:
        html_file.write("<html><body>Test</body></html>")
        html_path = html_file.name
    
    try:
        pdf_path = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
        
        # Test error handling
        with pytest.raises(requests.HTTPError, match="Gotenberg failed"):
            convert_to_pdf(html_path, pdf_path, "http://fake-gotenberg")
    finally:
        # Clean up
        if os.path.exists(html_path):
            os.unlink(html_path)
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)