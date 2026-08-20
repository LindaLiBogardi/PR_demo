import requests
import json
import pandas as pd

API_URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/LE/LE0201/LE0201EKO/Tema25"


def hamta_metadata(url: str) -> dict:

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

def bygg_query(ar: list[str], contents_code: str = "000002UX") -> dict:
    """Bygger ett PXWeb-query för valda år och tabellinnehåll."""
    return {
        "query": [
            {"code": "Hushallstyp", "selection": {"filter": "item",
             "values": ["sub", "smb", "ekub", "ekmb", "emub", "emmb", "tot"]}},
            {"code": "ContentsCode", "selection": {"filter": "item",
             "values": [contents_code]}},
            {"code": "Tid", "selection": {"filter": "item", "values": ar}},
        ],
        "response": {"format": "json"},
    }
    
def hamta_data(url: str, query: dict) -> dict:
    response = requests.post(url, json=query, timeout=10)
    if not response.ok:
        print("Felmeddelande från API:et:", response.text)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    # Steg 1: hämta metadata för att se vilka variabler och koder som finns
    metadata = hamta_metadata(API_URL)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))

    query = {
        "query": [
            {
                "code": "Hushallstyp",
                "selection": {
                    "filter": "item",
                    "values": ["sub", "smb", "ekub", "ekmb", "emub", "emmb", "tot"]
                }
            },
            {
                "code": "ContentsCode",
                "selection": {
                    "filter": "item",
                    "values": ["000002UX"]      # Antal
                }
            },
            {
                "code": "Tid",
                "selection": {
                    "filter": "item",
                    "values": ["2022", "2023", "2024"]
                }
            }
        ],
        "response": {
            "format": "json"
        }
    }

    raw_data = hamta_data(API_URL, query)
    print(json.dumps(raw_data, indent=2, ensure_ascii=False))
