import pytest
from app.models.user import User


@pytest.mark.asyncio
async def test_get_empty_portfolio(async_client, async_session):
    # Create a test user
    user = User(email="user@example.com", password_hash="hashedpass")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    response = await async_client.get(f"/portfolio/{user.id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["Current_Portfolio_Value"] == 0
    assert json_data["Portfolio_Details"] == []

