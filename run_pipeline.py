"""
Kör hela ELT-kedjan: hämta data → omvandla till DataFrame → spara som CSV.

Exempel:
    # Hämta färsk data från SCB:s API
    python run_pipeline.py --output resultat.csv

    # Kör mot sparad exempeldata (används i CI – inget nätverk krävs)
    python run_pipeline.py --input tests/exempel.json --output /tmp/resultat.csv
"""

import argparse
import json

from requests_SCB import API_URL, bygg_query, hamta_data
from transform_SCB import till_dataframe


def las_fran_fil(sokvag: str) -> dict:
    """Läser sparad JSON från disk istället för att anropa API:et."""
    with open(sokvag, encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Kör SCB-pipelinen.")
    parser.add_argument(
        "--input",
        help="Sökväg till sparad JSON-fil. Utan denna hämtas data från API:et.",
    )
    parser.add_argument(
        "--output",
        default="resultat.csv",
        help="Sökväg där resultatet sparas (standard: resultat.csv).",
    )
    args = parser.parse_args()

    # EXTRACT
    if args.input:
        print(f"Läser sparad data från {args.input}")
        raw_data = las_fran_fil(args.input)
    else:
        print(f"Hämtar data från {API_URL}")
        query = bygg_query(ar=["2022", "2023", "2024"])
        raw_data = hamta_data(API_URL, query)

    # TRANSFORM
    df = till_dataframe(raw_data)

    # LOAD
    df.to_csv(args.output, index=False)
    print(f"Sparade {len(df)} rader till {args.output}")


if __name__ == "__main__":
    main()