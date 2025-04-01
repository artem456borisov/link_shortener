# src/linker/tests/test_links.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.main import create_app
from src.linker.models import links_table, metadata
from src.linker.db import get_async_session
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
async_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def db_session():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        async with async_engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)

@pytest.fixture
def test_data():
    return {
        "full_link": "https://example.com",
        "short_link": "test123",
    }

@pytest.fixture
def client(db_session):
    # Mock Redis and Celery
    with patch("fastapi_cache.FastAPICache.init"), \
         patch("src.tasks.router") as mock_tasks:
        
        # Create test app with testing=True
        app = create_app(testing=True)
        app.dependency_overrides[get_async_session] = lambda: db_session
        
        with TestClient(app) as test_client:
            yield test_client

class TestLinkShorteningEndpoints:
    def test_create_short_link_success(self, client, test_data):
        response = client.post(
            "/links/shorten",
            json=test_data
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_get_original_link(self, client, test_data, db_session):
        client.post("/links/shorten", json=test_data)
        response = client.get(f"/links/{test_data['short_link']}")
        assert response.status_code == 200
        assert test_data["full_link"] in response.json()["data"][0]