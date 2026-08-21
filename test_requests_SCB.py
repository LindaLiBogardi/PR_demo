"""
Enhetstester för datahämtningen.

Inga riktiga API-anrop görs – bygg_query() är en ren funktion,
och hamta_data() testas med ett fejkat svar.
"""

import pytest

from requests_SCB import API_URL, bygg_query, hamta_data


# --- bygg_query: ren funktion, enkel att testa -----------------------------

def test_bygg_query_innehaller_valda_ar():
    query = bygg_query(ar=["2023", "2024"])
    tid = next(v for v in query["query"] if v["code"] == "Tid")
    assert tid["selection"]["values"] == ["2023", "2024"]


def test_bygg_query_har_alla_variabler():
    query = bygg_query(ar=["2024"])
    koder = [v["code"] for v in query["query"]]
    assert koder == ["Hushallstyp", "ContentsCode", "Tid"]


def test_bygg_query_efterfragar_json():
    query = bygg_query(ar=["2024"])
    assert query["response"]["format"] == "json"


def test_bygg_query_med_ett_enda_ar():
    """Gränsfall: en lista med ett värde ska fungera lika bra."""
    query = bygg_query(ar=["2024"])
    tid = next(v for v in query["query"] if v["code"] == "Tid")
    assert tid["selection"]["values"] == ["2024"]


# --- hamta_data: kräver nätverk, så vi ersätter anropet --------------------

class FejkatSvar:
    """Låtsas vara ett requests.Response-objekt."""

    def __init__(self, data, ok=True):
        self._data = data
        self.ok = ok
        self.text = "fejkat felmeddelande"

    def json(self):
        return self._data

    def raise_for_status(self):
        if not self.ok:
            raise Exception("HTTP-fel")


def test_hamta_data_returnerar_json(monkeypatch):
    """hamta_data ska ge tillbaka det API:et svarade, som en dict."""
    forvantat = {"columns": [], "data": []}

    def fejkad_post(url, json=None, timeout=None):
        return FejkatSvar(forvantat)

    monkeypatch.setattr("requests_SCB.requests.post", fejkad_post)

    resultat = hamta_data(API_URL, bygg_query(ar=["2024"]))
    assert resultat == forvantat


def test_hamta_data_kastar_fel_vid_dalig_status(monkeypatch):
    """Om API:et svarar med fel ska det inte tystas ner."""

    def fejkad_post(url, json=None, timeout=None):
        return FejkatSvar({}, ok=False)

    monkeypatch.setattr("requests_SCB.requests.post", fejkad_post)

    with pytest.raises(Exception):
        hamta_data(API_URL, bygg_query(ar=["2024"]))