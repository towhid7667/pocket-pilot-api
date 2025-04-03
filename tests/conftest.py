import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(scope="function")
async def client():
    # Create the client without closing it immediately
    client = AsyncClient(app=app, base_url="http://test")
    yield client
    # Explicitly close the client after the test
    await client.aclose()

@pytest.fixture(scope="function")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)