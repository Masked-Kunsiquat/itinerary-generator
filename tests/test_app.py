import pytest
from io import BytesIO
import sys
sys.path.insert(0, '.')
import app as app_module


@pytest.fixture
def client():
    app_module.app.config['TESTING'] = True
    with app_module.app.test_client() as client:
        yield client


def test_get_root(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"<form" in response.data  # crude check for rendered form


def test_post_missing_trip_file(client):
    response = client.post('/', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"Missing trip.json" in response.data


def test_post_with_trip_json_only(monkeypatch, client):
    monkeypatch.setattr(app_module, "generate_main", lambda: None)
    monkeypatch.setattr(app_module, "send_file", lambda path, **kwargs: ("MOCKED_PATH", 200, {}))

    trip_data = b'{ "trip": { "startDate": "2025-08-20", "endDate": "2025-08-26" } }'

    response = client.post('/', data={
        'trip_json': (BytesIO(trip_data), 'trip.json')
    }, content_type='multipart/form-data')

    assert response.status_code == 200 or isinstance(response, tuple)


def test_post_with_pdf_flag(monkeypatch, client):
    def mock_generate_main():
        assert '--pdf' in sys.argv
        assert 'http://gotenberg:3000/forms/chromium/convert/html' in sys.argv

    monkeypatch.setattr(app_module, "generate_main", mock_generate_main)
    monkeypatch.setattr(app_module, "send_file", lambda path, **kwargs: ("MOCKED_PDF", 200, {}))

    trip_data = b'{ "trip": { "startDate": "2025-08-20", "endDate": "2025-08-26" } }'

    response = client.post('/', data={
        'trip_json': (BytesIO(trip_data), 'trip.json'),
        'generate_pdf': 'on'
    }, content_type='multipart/form-data')

    assert response.status_code == 200 or isinstance(response, tuple)


def test_generate_main_failure(monkeypatch, client):
    def fail():
        raise RuntimeError("Boom!")

    monkeypatch.setattr(app_module, "generate_main", fail)

    trip_data = b'{ "trip": { "startDate": "2025-08-20", "endDate": "2025-08-26" } }'

    response = client.post('/', data={
        'trip_json': (BytesIO(trip_data), 'trip.json')
    }, content_type='multipart/form-data')

    assert response.status_code == 500
    assert b"An internal error occurred" in response.data

def test_post_with_custom_template(monkeypatch, client):
    monkeypatch.setattr(app_module, "generate_main", lambda: None)
    monkeypatch.setattr(app_module, "send_file", lambda path, **kwargs: ("MOCKED_PATH", 200, {}))

    trip_data = b'{ "trip": { "startDate": "2025-08-20", "endDate": "2025-08-26" } }'
    template_data = b"<html><body>{{ trip_name }}</body></html>"

    response = client.post('/', data={
        'trip_json': (BytesIO(trip_data), 'trip.json'),
        'template_html': (BytesIO(template_data), 'custom_template.html'),
    }, content_type='multipart/form-data')

    assert response.status_code == 200 or isinstance(response, tuple)
