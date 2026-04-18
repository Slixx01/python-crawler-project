import sys
import os
import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app

sys.path.insert(0, os.path.dirname(__file__))

@pytest.fixture()
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c