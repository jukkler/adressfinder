from unittest.mock import patch
from click.testing import CliRunner
from grundstuecksfinder.cli import main


def _geo():
    return {"bbox": "6.87,51.08,6.89,51.10", "lat": 51.09, "lon": 6.88}


def _features(flaeche=500, lagebeztxt="Teststr. 1"):
    return [{
        "properties": {
            "flaeche": flaeche, "lagebeztxt": lagebeztxt,
            "gemeinde": "Test", "kreis": "Testkreis",
            "flstkennz": "0511100", "tntxt": "Wohnbau;500",
        },
        "geometry": None,
    }]


@patch("grundstuecksfinder.cli.fetch_flurstuecke")
@patch("grundstuecksfinder.cli.geocode")
def test_cli_basic_search(mock_geocode, mock_fetch):
    mock_geocode.return_value = _geo()
    mock_fetch.return_value = _features()

    result = CliRunner().invoke(main, ["Teststadt", "-f", "500", "-t", "10"])
    assert result.exit_code == 0
    assert "Teststr. 1" in result.output
    assert "1 Treffer" in result.output


@patch("grundstuecksfinder.cli.fetch_flurstuecke")
@patch("grundstuecksfinder.cli.geocode")
def test_cli_no_matches(mock_geocode, mock_fetch):
    mock_geocode.return_value = _geo()
    mock_fetch.return_value = _features(flaeche=9999)

    result = CliRunner().invoke(main, ["Teststadt", "-f", "500"])
    assert result.exit_code == 0
    assert "Keine Treffer" in result.output


@patch("grundstuecksfinder.cli.fetch_flurstuecke")
@patch("grundstuecksfinder.cli.geocode")
def test_cli_csv_export(mock_geocode, mock_fetch, tmp_path):
    mock_geocode.return_value = _geo()
    mock_fetch.return_value = _features()
    csv_path = str(tmp_path / "out.csv")

    result = CliRunner().invoke(main, ["Ort", "-f", "500", "--csv", csv_path])
    assert result.exit_code == 0
    assert "CSV gespeichert" in result.output
    assert (tmp_path / "out.csv").exists()
