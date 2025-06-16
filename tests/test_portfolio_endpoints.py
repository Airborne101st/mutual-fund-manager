import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.db.session import get_session
from app.models.user import User
from app.models.fund import Fund
from app.models.portfolio import Portfolio

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = Session(engine)


# Dependency override
def override_get_session():
    with TestingSessionLocal as session:
        yield session


app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Create test user
        user = User(id=1, name="Test User", email="test@example.com", password_hash="somepassword")
        session.add(user)

        # Create test fund
        fund = Fund(id=1, fund_code="123ABC", fund_name="Test Fund", fund_family="Test Family", latest_nav=100.0)
        session.add(fund)

        # Create portfolio record
        portfolio = Portfolio(user_id=1, fund_id=1, units=10)
        session.add(portfolio)

        session.commit()
    yield
    SQLModel.metadata.drop_all(engine)


def test_get_portfolio_user():
    response = client.get("/portfolio/1")
    assert response.status_code == 200
    data = response.json()
    assert "Current_Portfolio_Value" in data
    assert data["Current_Portfolio_Value"] == 1000.0
    assert isinstance(data["Portfolio_Details"], list)
    assert data["Portfolio_Details"][0]["Fund_Name"] == "Test Fund"


def test_post_fund_units_existing_fund():
    body = {
        "fund_code": "123ABC",
        "units": 5,
        "user_id": 1
    }
    response = client.post("/portfolio/buy-fund", json=body)
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Updated 5 units in Test Fund" in response.json()["message"]


def test_post_fund_units_new_fund(monkeypatch):
    import app.routes.portfolio as portfolio_router
    # Mock RapidAPI response
    def mock_get_fund_details_by_fund_code(code: str):
        return [{
            "Scheme_Name": "New Test Fund",
            "Mutual_Fund_Family": "New Test Family",
            "Net_Asset_Value": "50.0"
        }]

    monkeypatch.setattr(portfolio_router, "get_fund_details_by_fund_code", mock_get_fund_details_by_fund_code)

    body = {
        "fund_code": "NEW123",
        "units": 2,
        "user_id": 1
    }
    response = client.post("/portfolio/buy-fund", json=body)
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Added 2 units to New Test Fund" in response.json()["message"]
