import pytest
import pytest_asyncio
from backend.app import app as quart_app

@pytest_asyncio.fixture
async def app():
    yield quart_app

@pytest_asyncio.fixture
async def client(app):
    return app.test_client()
