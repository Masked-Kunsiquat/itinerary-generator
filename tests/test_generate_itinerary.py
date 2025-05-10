import os
import tempfile
from unittest.mock import patch, MagicMock

from itinerary_generator.generate_itinerary import generate_itinerary, main


def test_generate_itinerary_html_only(fake_json_file, fake_template_file):
    """Test generating an itinerary with HTML output only."""
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as output_file:
        output_path = output_file.name
    
    try:
        # Generate the itinerary
        html_path, pdf_path = generate_itinerary(
            json_path=fake_json_file,
            template_path=fake_template_file,
            output_html=output_path
        )
        
        # Check the result
        assert html_path == output_path
        assert pdf_path is None
        assert os.path.exists(output_path)
        
        # Check content
        with open(output_path, 'r') as f:
            content = f.read()
            assert "Test Trip" in content
    finally:
        # Clean up
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_generate_itinerary_with_pdf(fake_json_file, fake_template_file):
    """Test generating an itinerary with both HTML and PDF output."""
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as html_file:
        html_path = html_file.name
    
    pdf_path = html_path.replace('.html', '.pdf')
    
    try:
        # The critical fix: patch the actual module import path
        # This ensures we patch the function that's actually called
        with patch('itinerary_generator.generate_itinerary.convert_to_pdf') as mock_pdf:
            # Configure the mock to return the pdf_path
            mock_pdf.return_value = pdf_path
            
            # Write a fake PDF file to simulate the conversion
            with open(pdf_path, 'wb') as f:
                f.write(b'%PDF-1.5 test content')
            
            # Generate the itinerary
            html_result, pdf_result = generate_itinerary(
                json_path=fake_json_file,
                template_path=fake_template_file,
                output_html=html_path,
                pdf_path=pdf_path,
                gotenberg_url="http://test-gotenberg:3000"  # Even with a bad URL, test should pass
            )
            
            # Check the result
            assert html_result == html_path
            assert pdf_result == pdf_path
            assert os.path.exists(html_path)
            assert os.path.exists(pdf_path)
            
            # Verify convert_to_pdf was called with the right arguments
            mock_pdf.assert_called_once_with(html_path, pdf_path, "http://test-gotenberg:3000")
    finally:
        # Clean up
        if os.path.exists(html_path):
            os.unlink(html_path)
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)


def test_main_function():
    """Test the main CLI function."""
    with patch('argparse.ArgumentParser.parse_args') as mock_args, \
         patch('itinerary_generator.generate_itinerary.generate_itinerary') as mock_generate:
        
        # Set up mock arguments
        args = MagicMock()
        args.json_path = "trip.json"
        args.template_path = "template.html"
        args.output_html = "output.html"
        args.pdf = "output.pdf"
        args.gotenberg_url = "http://gotenberg:3000"
        args.timezone = "UTC"  # Add timezone argument
        mock_args.return_value = args
        
        # Mock the generate_itinerary function
        mock_generate.return_value = ("output.html", "output.pdf")
        
        # Call the main function
        main()
        
        # Verify the generate_itinerary function was called with expected args, including timezone
        mock_generate.assert_called_once_with(
            json_path="trip.json",
            template_path="template.html",
            output_html="output.html",
            pdf_path="output.pdf",
            gotenberg_url="http://gotenberg:3000",
            user_timezone="UTC"
        )


def test_main_function_no_pdf():
    """Test the main CLI function without PDF output."""
    with patch('argparse.ArgumentParser.parse_args') as mock_args, \
         patch('itinerary_generator.generate_itinerary.generate_itinerary') as mock_generate:
        
        # Set up mock arguments
        args = MagicMock()
        args.json_path = "trip.json"
        args.template_path = "template.html"
        args.output_html = "output.html"
        args.pdf = None
        args.gotenberg_url = "http://gotenberg:3000"
        args.timezone = None  # No timezone specified
        mock_args.return_value = args
        
        # Mock the generate_itinerary function
        mock_generate.return_value = ("output.html", None)
        
        # Call the main function
        main()
        
        # Verify the generate_itinerary function was called with expected args
        mock_generate.assert_called_once_with(
            json_path="trip.json",
            template_path="template.html",
            output_html="output.html",
            pdf_path=None,
            gotenberg_url="http://gotenberg:3000",
            user_timezone=None
        )