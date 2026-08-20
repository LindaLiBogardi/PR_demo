import pandas as pd

from requests_SCB import API_URL, hamta_data, bygg_query


def till_dataframe(raw_json: dict) -> pd.DataFrame:
    
    kolumnnamn = [kol["text"] for kol in raw_json["columns"]]
    rader = [post["key"] + post["values"] for post in raw_json["data"]]

    df = pd.DataFrame(rader, columns=kolumnnamn)
    matvarden = [kol["text"] for kol in raw_json["columns"] if kol["type"] == "c"]
    for kolumn in matvarden:
        df[kolumn] = pd.to_numeric(df[kolumn], errors="coerce")

    return df


if __name__ == "__main__":
    query = bygg_query(ar=["2022", "2023", "2024"])
    raw_data = hamta_data(API_URL, query)

    df = till_dataframe(raw_data)
    print(df.head(10))
    print(df.dtypes)