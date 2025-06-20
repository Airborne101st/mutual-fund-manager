import pytest

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"

@pytest.mark.asyncio
async def test_register_success(async_client):
    response = await async_client.post(REGISTER_URL, json={
        "email": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_register_existing_user(async_client):
    # Register once
    await async_client.post(REGISTER_URL, json={
        "email": "test2@example.com",
        "password": "testpass"
    })

    # Register again
    response = await async_client.post(REGISTER_URL, json={
        "email": "test2@example.com",
        "password": "testpass"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_success(async_client):
    # First register the user
    await async_client.post(REGISTER_URL, json={
        "email": "test3@example.com",
        "password": "secret123"
    })

    # Then login
    response = await async_client.post(LOGIN_URL, json={
        "email": "test3@example.com",
        "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_login_invalid_email(async_client):
    response = await async_client.post(LOGIN_URL, json={
        "email": "notfound@example.com",
        "password": "irrelevant"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_invalid_password(async_client):
    # Register user
    await async_client.post(REGISTER_URL, json={
        "email": "test4@example.com",
        "password": "correctpass"
    })

    # Try wrong password
    response = await async_client.post(LOGIN_URL, json={
        "email": "test4@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

