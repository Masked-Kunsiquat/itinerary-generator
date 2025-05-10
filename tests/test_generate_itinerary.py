import os
import tempfile
from unittest.mock import patch, MagicMock
import pytest # Added this import
import json   # Added this import for the malformed_json_key_error test
import logging

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
        html_path_arg = html_file.name # Renamed to avoid conflict in this scope
    
    pdf_path_arg = html_path_arg.replace('.html', '.pdf') # Renamed
    
    try:
        # The critical fix: patch the actual module import path
        # This ensures we patch the function that's actually called
        with patch('itinerary_generator.generate_itinerary.convert_to_pdf') as mock_pdf:
            # Configure the mock to return the pdf_path
            mock_pdf.return_value = pdf_path_arg # Use renamed variable
            
            # Write a fake PDF file to simulate the conversion
            with open(pdf_path_arg, 'wb') as f: # Use renamed variable
                f.write(b'%PDF-1.5 test content')
            
            # Generate the itinerary
            html_result, pdf_result = generate_itinerary(
                json_path=fake_json_file,
                template_path=fake_template_file,
                output_html=html_path_arg, # Use renamed variable
                pdf_path=pdf_path_arg,     # Use renamed variable
                gotenberg_url="http://test-gotenberg:3000"
            )
            
            # Check the result
            assert html_result == html_path_arg
            assert pdf_result == pdf_path_arg
            assert os.path.exists(html_path_arg)
            assert os.path.exists(pdf_path_arg)
            
            # Verify convert_to_pdf was called with the right arguments
            mock_pdf.assert_called_once_with(html_path_arg, pdf_path_arg, "http://test-gotenberg:3000")
    finally:
        # Clean up
        if os.path.exists(html_path_arg): # Use renamed variable
            os.unlink(html_path_arg)
        if os.path.exists(pdf_path_arg):   # Use renamed variable
            os.unlink(pdf_path_arg)


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
        args.timezone = "UTC"
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
        args.timezone = None
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

def test_generate_itinerary_pdf_conversion_fails(fake_json_file, fake_template_file, caplog): # Add caplog fixture
    """Test HTML is generated and warning logged if PDF conversion fails."""
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as html_file:
        html_path_arg = html_file.name
    pdf_path_arg = html_path_arg.replace('.html', '.pdf')

    try:
        # Only need to patch convert_to_pdf for this test's purpose
        with patch('itinerary_generator.generate_itinerary.convert_to_pdf', side_effect=Exception("PDF boom!")):
            caplog.set_level(logging.WARNING) # Ensure WARNING level messages are captured by caplog

            html_result, pdf_result = generate_itinerary(
                json_path=fake_json_file,
                template_path=fake_template_file,
                output_html=html_path_arg,
                pdf_path=pdf_path_arg, # Request PDF
                gotenberg_url="http://fake-gotenberg"
            )

            assert os.path.exists(html_result)
            assert pdf_result is None
            
            # Check logs using caplog
            assert len(caplog.records) == 1 # Check that one log message was recorded
            record = caplog.records[0]
            assert record.levelname == "WARNING"
            assert "PDF conversion failed: PDF boom!" in record.message
            assert "HTML output is still available" in record.message
    finally:
        if os.path.exists(html_path_arg): os.unlink(html_path_arg)
        if os.path.exists(pdf_path_arg): os.unlink(pdf_path_arg)

def test_generate_itinerary_json_not_found(fake_template_file):
    """Test FileNotFoundError if JSON path is invalid."""
    with pytest.raises(FileNotFoundError) as excinfo:
        generate_itinerary(
            json_path="non_existent_trip.json",
            template_path=fake_template_file,
            output_html="test_output.html"
        )
    assert "Failed to generate itinerary" in str(excinfo.value)
    # Check the cause of the re-raised exception
    if excinfo.value.__cause__:
        assert "Trip data file not found" in str(excinfo.value.__cause__)


def test_generate_itinerary_malformed_json_key_error(fake_template_file):
    """Test ValueError for malformed JSON (missing key)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_json:
        # Create JSON missing the top-level "trip" key
        json.dump({ "name_of_trip": "Missing trip key" }, tmp_json)
        malformed_json_path = tmp_json.name
    
    try:
        with pytest.raises(ValueError) as excinfo: # Expecting ValueError due to re-raise
            generate_itinerary(
                json_path=malformed_json_path,
                template_path=fake_template_file,
                output_html="test_output.html"
            )
        # Check the message of the ValueError, which should indicate the original KeyError
        assert "Invalid trip data structure, missing key: 'trip'" in str(excinfo.value)
    finally:
        os.unlink(malformed_json_path)

def test_generate_itinerary_generic_runtime_error(fake_json_file, fake_template_file):
    """Test RuntimeError for unexpected errors during generation."""
    # Patch a function called early in generate_itinerary to raise an error
    with patch('itinerary_generator.generate_itinerary.parse_dates', side_effect=RuntimeError("Generic parse boom!")):
        with pytest.raises(RuntimeError) as excinfo:
            generate_itinerary(
                json_path=fake_json_file,
                template_path=fake_template_file,
                output_html="test_output.html"
            )
        assert "Unexpected error generating itinerary: Generic parse boom!" in str(excinfo.value)