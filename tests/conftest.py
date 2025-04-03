import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(scope="function")
async def client():
    client = AsyncClient(app=app, base_url="http://test")
    yield client
    await client.aclose()

@pytest.fixture(scope="function")
async def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)