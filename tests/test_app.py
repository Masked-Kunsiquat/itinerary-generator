import pytest
from io import BytesIO
import sys
import os
from unittest.mock import patch, MagicMock

from itinerary_generator.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Patch the get_common_timezones function to avoid timezone validation during tests
@pytest.fixture(autouse=True)
def mock_get_common_timezones():
    with patch('itinerary_generator.app.get_common_timezones', return_value=["UTC", "America/New_York"]):
        yield


def test_get_root(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"<form" in response.data


def test_post_missing_trip_file(client):
    response = client.post('/', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"Missing trip.json" in response.data


def test_post_with_trip_json_only(client):
    with patch('itinerary_generator.app.generate_itinerary') as mock_generate, \
         patch('itinerary_generator.app.send_file', return_value=("MOCKED_PATH", 200, {})) as mock_send:
        
        # Set up the mock to return HTML path only
        mock_generate.return_value = ("output.html", None)
        
        trip_data = b'{ "trip": { "startDate": "2025-08-20", "endDate": "2025-08-26" } }'

        response = client.post('/', data={
            'trip_json': (BytesIO(trip_data), 'trip.json')
        }, content_type='multipart/form-data')

        assert response.status_code == 200
        mock_generate.assert_called_once()
        mock_send.assert_called_once()


def test_post_with_pdf_flag(client):
    with patch('itinerary_generator.app.generate_itinerary') as mock_generate, \
         patch('itinerary_generator.app.send_file', return_value=("MOCKED_PDF", 200, {})) as mock_send:
        
        # Set up the mock to return both HTML and PDF paths
        mock_generate.return_value = ("output.html", "output.pdf")

        trip_data = b'{ "trip": { "startDate": "2025-08-20", "endDate": "2025-08-26" } }'

        response = client.post('/', data={
            'trip_json': (BytesIO(trip_data), 'trip.json'),
            'generate_pdf': 'on'
        }, content_type='multipart/form-data')

        assert response.status_code == 200
        mock_generate.assert_called_once()
        
        # Check that we returned the PDF file
        args, kwargs = mock_send.call_args
        assert args[0] == "output.pdf"


def test_generate_main_failure(client):
    with patch('itinerary_generator.app.generate_itinerary') as mock_generate:
        # Set up the mock to raise an exception
        mock_generate.side_effect = RuntimeError("Test Error")

        trip_data = b'{ "trip": { "startDate": "2025-08-20", "endDate": "2025-08-26" } }'

        response = client.post('/', data={
            'trip_json': (BytesIO(trip_data), 'trip.json')
        }, content_type='multipart/form-data')

        assert response.status_code == 500
        assert b"An internal error occurred" in response.data


def test_post_with_custom_template(client):
    with patch('itinerary_generator.app.generate_itinerary') as mock_generate, \
         patch('itinerary_generator.app.send_file', return_value=("MOCKED_PATH", 200, {})) as mock_send:
        
        # Set up the mock to return HTML path only
        mock_generate.return_value = ("output.html", None)

        trip_data = b'{ "trip": { "startDate": "2025-08-20", "endDate": "2025-08-26" } }'
        template_data = b"<html><body>{{ trip_name }}</body></html>"

        response = client.post('/', data={
            'trip_json': (BytesIO(trip_data), 'trip.json'),
            'template_html': (BytesIO(template_data), 'custom_template.html'),
        }, content_type='multipart/form-data')

        assert response.status_code == 200
        mock_generate.assert_called_once()
        mock_send.assert_called_once()