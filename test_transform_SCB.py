"""
Enhetstester för omvandlingen JSON → DataFrame.

Ingen kontakt med API:et – all testdata är påhittad,
men har exakt samma struktur som SCB:s svar.
"""

import pandas as pd
import pytest

from transform_SCB import till_dataframe


@pytest.fixture
def fejkad_json():
    """Ett minimalt API-svar med samma struktur som SCB:s."""
    return {
        "columns": [
            {"code": "Hushallstyp", "text": "hushållstyp", "type": "d"},
            {"code": "Tid", "text": "år", "type": "t"},
            {"code": "000002UX", "text": "Antal", "type": "c"},
        ],
        "data": [
            {"key": ["sub", "2024"], "values": ["4171"]},
            {"key": ["smb", "2024"], "values": ["11572"]},
            {"key": ["tot", "2024"], "values": ["15743"]},
        ],
    }


def test_ger_ratt_kolumnnamn(fejkad_json):
    df = till_dataframe(fejkad_json)
    assert list(df.columns) == ["hushållstyp", "år", "Antal"]


def test_ger_en_rad_per_datapunkt(fejkad_json):
    df = till_dataframe(fejkad_json)
    assert len(df) == 3


def test_behaller_dimensionsvarden(fejkad_json):
    """key-listan ska hamna i dimensionskolumnerna, i rätt ordning."""
    df = till_dataframe(fejkad_json)
    assert df.loc[0, "hushållstyp"] == "sub"
    assert df.loc[0, "år"] == "2024"


def test_gor_om_text_till_siffror(fejkad_json):
    """SCB skickar allt som text – mätvärden måste bli numeriska."""
    df = till_dataframe(fejkad_json)
    assert pd.api.types.is_numeric_dtype(df["Antal"])
    assert df.loc[0, "Antal"] == 4171


def test_dimensioner_forblir_text(fejkad_json):
    """År ska INTE bli ett tal – det är en kategori, inte ett mätvärde."""
    df = till_dataframe(fejkad_json)
    assert not pd.api.types.is_numeric_dtype(df["år"])


def test_hanterar_saknade_varden():
    """'..' betyder saknat värde hos SCB och ska bli NaN, inte krascha."""
    json_med_lucka = {
        "columns": [
            {"code": "Tid", "text": "år", "type": "t"},
            {"code": "000002UX", "text": "Antal", "type": "c"},
        ],
        "data": [
            {"key": ["2023"], "values": ["100"]},
            {"key": ["2024"], "values": [".."]},
        ],
    }
    df = till_dataframe(json_med_lucka)
    assert df.loc[0, "Antal"] == 100
    assert pd.isna(df.loc[1, "Antal"])


def test_tom_data_ger_tom_dataframe():
    """Gränsfall: API:et svarade utan rader."""
    tom_json = {
        "columns": [
            {"code": "Tid", "text": "år", "type": "t"},
            {"code": "000002UX", "text": "Antal", "type": "c"},
        ],
        "data": [],
    }
    df = till_dataframe(tom_json)
    assert len(df) == 0