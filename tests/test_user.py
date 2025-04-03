import pytest
from httpx import AsyncClient
from app.utils.auth import get_redis

@pytest.mark.asyncio
async def test_register_and_verify(client: AsyncClient, setup_db):
    response = await client.post("/user/register", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "profile_picture_url": "http://example.com/pic.jpg"
    })
    assert response.status_code == 200
    user_id = response.json()["user_id"]

    redis_client = await get_redis()
    otp = await redis_client.get(f"otp:{user_id}")
    response = await client.post("/user/verify", json={"user_id": user_id, "otp": otp})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login_logout(client: AsyncClient, setup_db):
    # Register once
    response = await client.post("/user/register", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    })
    assert response.status_code == 200
    user_id = response.json()["user_id"]

    redis_client = await get_redis()
    otp = await redis_client.get(f"otp:{user_id}")
    await client.post("/user/verify", json={"user_id": user_id, "otp": otp})

    response = await client.post("/user/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert "access_token" in response.cookies

    response = await client.post("/user/logout", cookies={"access_token": token})
    assert response.status_code == 200
    assert "access_token" not in response.cookies

    response = await client.get(f"/user/{user_id}", cookies={"access_token": token})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token blacklisted"

@pytest.mark.asyncio
async def test_user_operations(client: AsyncClient, setup_db):
    response = await client.post("/user/register", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "profile_picture_url": "http://example.com/pic.jpg"
    })
    user_id = response.json()["user_id"]
    redis_client = await get_redis()
    otp = await redis_client.get(f"otp:{user_id}")
    await client.post("/user/verify", json={"user_id": user_id, "otp": otp})

    response = await client.post("/user/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = await client.get(f"/user/{user_id}", cookies={"access_token": token})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

    response = await client.get("/user/", cookies={"access_token": token})
    assert response.status_code == 200
    assert len(response.json()["users"]) > 0

    response = await client.put(f"/user/{user_id}", json={
        "name": "Updated User",
        "profile_picture_url": "http://example.com/newpic.jpg",
        "password": "newpassword456"
    }, cookies={"access_token": token})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated User"

    response = await client.post("/user/login", json={
        "email": "test@example.com",
        "password": "newpassword456"
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient, setup_db):
    response = await client.post("/user/register", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    })
    user_id = response.json()["user_id"]
    redis_client = await get_redis()
    otp = await redis_client.get(f"otp:{user_id}")
    await client.post("/user/verify", json={"user_id": user_id, "otp": otp})

    response = await client.post("/user/forgot-password", json={"email": "test@example.com"})
    assert response.status_code == 200
    user_id = response.json()["user_id"]

    reset_otp = await redis_client.get(f"reset_otp:{user_id}")
    response = await client.post("/user/reset-password", json={
        "email": "test@example.com",
        "otp": reset_otp,
        "new_password": "resetpassword789"
    })
    assert response.status_code == 200

    response = await client.post("/user/login", json={
        "email": "test@example.com",
        "password": "resetpassword789"
    })
    assert response.status_code == 200