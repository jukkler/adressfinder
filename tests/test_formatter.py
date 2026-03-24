import os
from grundstuecksfinder.formatter import format_table, export_csv


def _match(adresse="Teststraße 1", flaeche=500, abweichung=0.0):
    return {
        "adresse": adresse,
        "flaeche": flaeche,
        "abweichung": abweichung,
        "gemeinde": "Teststadt",
        "kreis": "Testkreis",
        "flstkennz": "05111000100001______",
        "nutzung": "Wohnbaufläche;500",
        "geometrie": None,
    }


def test_format_table_empty():
    assert "Keine Treffer" in format_table([])


def test_format_table_shows_rows():
    table = format_table([
        _match(),
        _match(adresse="Andere Str. 2", flaeche=510, abweichung=2.0),
    ])
    assert "Teststraße 1" in table
    assert "Andere Str. 2" in table
    assert "500" in table


def test_format_table_cleans_nutzung():
    table = format_table([_match()])
    # Should show "Wohnbaufläche" not "Wohnbaufläche;500"
    assert "Wohnbaufläche" in table
    assert ";500" not in table


def test_export_csv(tmp_path):
    path = str(tmp_path / "test.csv")
    export_csv([_match(), _match(adresse="Zweite Str.")], path)
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "Teststraße 1" in content
    assert "Zweite Str." in content
    assert "adresse" in content  # header row
