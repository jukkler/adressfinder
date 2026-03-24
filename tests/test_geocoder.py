import pytest
from conftest import make_response


def test_geocode_returns_bbox_and_center(mock_httpx):
    mock_httpx(make_response([{
        "lat": "51.09",
        "lon": "6.88",
        "boundingbox": ["51.08", "51.10", "6.87", "6.89"],
    }]))
    from grundstuecksfinder.geocoder import geocode

    result = geocode("Monheim am Rhein")
    assert result["bbox"] == "6.87,51.08,6.89,51.10"
    assert result["lat"] == 51.09
    assert result["lon"] == 6.88


def test_geocode_no_results_raises(mock_httpx):
    mock_httpx(make_response([]))
    from grundstuecksfinder.geocoder import geocode

    with pytest.raises(ValueError, match="Keine Ergebnisse"):
        geocode("Nichtexistierendestadt12345")


def test_geocode_with_radius_overrides_bbox(mock_httpx):
    mock_httpx(make_response([{
        "lat": "51.0",
        "lon": "7.0",
        "boundingbox": ["50.0", "52.0", "6.0", "8.0"],
    }]))
    from grundstuecksfinder.geocoder import geocode

    result = geocode("Köln", radius_m=1000)
    # radius=1000m should produce a small bbox, not the huge geocoder bbox
    parts = [float(x) for x in result["bbox"].split(",")]
    assert parts[0] > 6.0   # min_lon much larger than geocoder bbox
    assert parts[2] < 8.0   # max_lon much smaller
    # 2000m width / ~70km per degree at 51°N ≈ ~0.029°
    assert abs(parts[2] - parts[0]) < 0.1
