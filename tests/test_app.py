import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_shorten_url(client):
    response = client.post('/shorten', data={'url': 'https://example.com'})
    assert response.status_code == 200
    assert 'shortened_url' in response.get_data(as_text=True)

def test_redirect(client):
    client.post('/shorten', data={'url': 'https://example.com'})
    response = client.get('/abc123')
    assert response.status_code == 302

def test_invalid_url(client):
    response = client.post('/shorten', data={'url': 'invalid-url'})
    assert response.status_code == 400

def test_api(client):
    response = client.post('/api/shorten', 
                          json={'url': 'https://api.example.com'})
    assert response.status_code == 201
    assert 'short_url' in response.json