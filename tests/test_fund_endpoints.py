import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

client = TestClient(app)


def test_get_funds_by_family_success(monkeypatch):
    mock_response = [{"Scheme_Name": "Sample Fund 1"}, {"Scheme_Name": "Sample Fund 2"}]

    def mock_get_funds_by_family(family: str):
        return mock_response

    from app.routes import funds
    monkeypatch.setattr(funds, "get_funds_by_family", mock_get_funds_by_family)

    response = client.get("/funds/family/HDFC")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_response


def test_get_fund_by_code_success(monkeypatch):
    mock_response = {"Scheme_Name": "HDFC Equity Fund", "NAV": "102.55"}

    def mock_get_fund_details_by_fund_code(code: str):
        return mock_response

    from app.routes import funds
    monkeypatch.setattr(funds, "get_fund_details_by_fund_code", mock_get_fund_details_by_fund_code)

    response = client.get("/funds/code/102345")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_response


def test_get_fund_by_code_not_found(monkeypatch):
    from fastapi import HTTPException

    def mock_get_fund_details_by_fund_code(code: str):
        raise HTTPException(status_code=404, detail="No fund found")

    from app.routes import funds
    monkeypatch.setattr(funds, "get_fund_details_by_fund_code", mock_get_fund_details_by_fund_code)

    response = client.get("/funds/code/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "No fund found"
