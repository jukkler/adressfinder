import os
from grundstuecksfinder.map_export import export_map


def test_export_map_creates_html(tmp_path):
    matches = [{
        "adresse": "Teststr. 1",
        "flaeche": 500,
        "nutzung": "Wohnbau",
        "geometrie": {
            "type": "MultiPolygon",
            "coordinates": [[[[6.87, 51.08], [6.88, 51.08], [6.88, 51.09], [6.87, 51.09], [6.87, 51.08]]]],
        },
    }]
    path = str(tmp_path / "karte.html")
    export_map(matches, center_lat=51.085, center_lon=6.875, filepath=path)
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        html = f.read()
    assert "leaflet" in html.lower()


def test_export_map_empty_matches(tmp_path):
    path = str(tmp_path / "karte.html")
    export_map([], center_lat=51.0, center_lon=7.0, filepath=path)
    assert os.path.exists(path)
