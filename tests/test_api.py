import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from api.main import app
import os
from dotenv import load_dotenv

load_dotenv()
VALID_KEY = os.getenv("API_KEY")
HEADERS = {"X-API-KEY": VALID_KEY}


@pytest.mark.asyncio
async def test_books_no_api_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/books")
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_books_invalid_api_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/books", headers={"X-API-KEY": "wrongkey"})
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_book_invalid_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/books/invalidid123", headers=HEADERS)
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_changes_no_api_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/changes")
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_books_returns_list():
    with patch("api.main.book_collection") as mock_col:
        mock_col.aggregate.return_value.to_list = AsyncMock(return_value=[])
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/books", headers=HEADERS)
            assert response.status_code == 200
            assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_books_pagination():
    with patch("api.main.book_collection") as mock_col:
        mock_col.aggregate.return_value.to_list = AsyncMock(return_value=[])
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/books?page=1&limit=5", headers=HEADERS)
            assert response.status_code == 200

@pytest.mark.asyncio
async def test_books_filter_by_rating():
    with patch("api.main.book_collection") as mock_col:
        mock_col.aggregate.return_value.to_list = AsyncMock(return_value=[])
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/books?rating=5", headers=HEADERS)
            assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_book_not_found():
    with patch("api.main.book_collection") as mock_col:
        mock_col.find_one = AsyncMock(return_value=None)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/books/507f1f77bcf86cd799439011", headers=HEADERS)
            assert response.status_code == 404

@pytest.mark.asyncio
async def test_changes_returns_list():
    with patch("api.main.change_log_detection") as mock_col:
        mock_col.find.return_value.to_list = AsyncMock(return_value=[])
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/changes", headers=HEADERS)
            assert response.status_code == 200
            assert isinstance(response.json(), list)