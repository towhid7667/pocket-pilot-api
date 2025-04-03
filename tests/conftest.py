import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.database import Base, engine
from redis.asyncio import Redis

pytest_plugins = ['pytest_asyncio']

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
async def redis_client():
    client = Redis(host='localhost', port=6379, db=0)
    yield client
    await client.flushdb()
    await client.close()
    await client.connection_pool.disconnect()