import requests
import os
from dotenv import load_dotenv

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
    response = requests.get(url, headers=headers, params=parameters)
    return response.json()

def get_fund_details_by_fund_code(fund_code: str):
    url = f"https://{RAPIDAPI_HOST}/latest"
    parameters = {
        "Scheme_Type": "Open",
        "Scheme_Code": fund_code
    }
    response = requests.get(url, headers=headers, params=parameters)
    return response.json()