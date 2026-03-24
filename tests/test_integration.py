# tests/test_integration.py
from unittest.mock import patch, Mock
from click.testing import CliRunner
from grundstuecksfinder.cli import main


def _nominatim_response():
    resp = Mock()
    resp.json.return_value = [{
        "lat": "51.09", "lon": "6.88",
        "boundingbox": ["51.08", "51.10", "6.87", "6.89"],
    }]
    resp.raise_for_status.return_value = None
    return resp


def _lika_response():
    resp = Mock()
    resp.json.return_value = {
        "type": "FeatureCollection",
        "features": [
            {
                "properties": {
                    "flaeche": 595,
                    "lagebeztxt": "Hauptstraße 12",
                    "gemeinde": "Monheim am Rhein",
                    "kreis": "Mettmann",
                    "flstkennz": "05438300200075______",
                    "tntxt": "Wohnbaufläche;595",
                },
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [[[[6.87, 51.08], [6.88, 51.08], [6.88, 51.09], [6.87, 51.08]]]],
                },
            },
            {
                "properties": {
                    "flaeche": 100,
                    "lagebeztxt": "Kleine Gasse 1",
                    "gemeinde": "Monheim am Rhein",
                    "kreis": "Mettmann",
                    "flstkennz": "05438300200076______",
                    "tntxt": "Wohnbaufläche;100",
                },
                "geometry": None,
            },
        ],
        "links": [],
    }
    resp.raise_for_status.return_value = None
    return resp


@patch("httpx.get")
def test_full_pipeline(mock_get):
    # First call = Nominatim, second call = LIKA
    mock_get.side_effect = [_nominatim_response(), _lika_response()]

    result = CliRunner().invoke(main, ["Monheim am Rhein, Baumberg", "-f", "600", "-t", "10"])

    assert result.exit_code == 0
    assert "Hauptstraße 12" in result.output
    assert "595" in result.output
    assert "1 Treffer" in result.output
    # 100 m² parcel should NOT appear (way outside 540-660 m² range)
    assert "Kleine Gasse" not in result.output
