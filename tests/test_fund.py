import pytest
from fastapi import HTTPException
from unittest.mock import patch

FUND_FAMILY_URL = "/funds/family"
FUND_CODE_URL = "/funds/code"

@pytest.mark.asyncio
@patch("app.routes.funds.get_funds_by_family")
async def test_get_funds_by_family_success(mock_get_funds_by_family, async_client):
    mock_funds = [
        {
            "fund_code": "F123",
            "fund_name": "Growth Fund",
            "fund_family": "Growth House",
            "Net_Asset_Value": 200.0
        }
    ]
    mock_get_funds_by_family.return_value = mock_funds

    response = await async_client.get(f"{FUND_FAMILY_URL}/Growth House")
    assert response.status_code == 200
    assert response.json() == mock_funds
    mock_get_funds_by_family.assert_called_once_with("Growth House")


@pytest.mark.asyncio
@patch("app.routes.funds.get_funds_by_family")
async def test_get_funds_by_family_not_found(mock_get_funds_by_family, async_client):
    mock_get_funds_by_family.side_effect = HTTPException(status_code=404, detail="Fund family not found")

    response = await async_client.get(f"{FUND_FAMILY_URL}/Unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "Fund family not found"


@pytest.mark.asyncio
@patch("app.routes.funds.get_fund_details_by_fund_code")
async def test_get_fund_by_code_success(mock_get_fund_details, async_client):
    mock_fund = {
        "fund_code": "ABC123",
        "fund_name": "Alpha Equity Fund",
        "fund_family": "Alpha Group",
        "Net_Asset_Value": 123.45
    }
    mock_get_fund_details.return_value = mock_fund

    response = await async_client.get(f"{FUND_CODE_URL}/ABC123")
    assert response.status_code == 200
    assert response.json() == mock_fund
    mock_get_fund_details.assert_called_once_with("ABC123")


@pytest.mark.asyncio
@patch("app.routes.funds.get_fund_details_by_fund_code")
async def test_get_fund_by_code_not_found(mock_get_fund_details, async_client):
    mock_get_fund_details.side_effect = HTTPException(status_code=404, detail="Fund not found")

    response = await async_client.get(f"{FUND_CODE_URL}/INVALID123")
    assert response.status_code == 404
    assert response.json()["detail"] == "Fund not found"
