import requests
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST
}

def get_funds_by_family(family: str):
    url = f"https://{RAPIDAPI_HOST}/latest"
    parameters = {
        "Scheme_Type": "Open",
        "Mutual_Fund_Family": family
    }
    try:
        response = requests.get(url, headers=headers, params=parameters, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise HTTPException(status_code=404, detail="No funds found for the given family.")
        return data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"External API request failed: {str(e)}")


def get_fund_details_by_fund_code(fund_code: str):
    url = f"https://{RAPIDAPI_HOST}/latest"
    parameters = {
        "Scheme_Type": "Open",
        "Scheme_Code": fund_code
    }
    try:
        response = requests.get(url, headers=headers, params=parameters, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise HTTPException(status_code=404, detail="No fund found with the given code.")
        return data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"External API request failed: {str(e)}")
