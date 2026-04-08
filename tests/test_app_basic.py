import pytest

@pytest.mark.asyncio
async def test_home(client):
    """Test that the home page loads correctly."""
    response = await client.get('/')
    assert response.status_code == 200
    data = await response.get_data()
    assert b"Influenze Relay" in data or b"Let's Get Started" in data

@pytest.mark.asyncio
async def test_connect_route(client):
    """Test that the connect page loads."""
    response = await client.get('/connect')
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_form_route(client):
    """Test that the form page loads."""
    response = await client.get('/form')
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_progress_route(client):
    """Test that the progress page loads."""
    response = await client.get('/progress')
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_summary_route(client):
    """Test that the summary page loads."""
    response = await client.get('/summary')
    assert response.status_code == 200
