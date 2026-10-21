import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "a@test.com", "password": "secret123"},
    )
    assert r.status_code == 201
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "a@test.com", "password": "secret123"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()
