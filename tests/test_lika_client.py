from conftest import make_response


def _feature(flaeche, lagebeztxt="Teststraße 1"):
    return {
        "type": "Feature",
        "properties": {"flaeche": flaeche, "lagebeztxt": lagebeztxt, "gemeinde": "Test"},
        "geometry": {"type": "MultiPolygon", "coordinates": []},
    }


def test_fetch_single_page(mock_httpx):
    mock_httpx(make_response({
        "type": "FeatureCollection",
        "features": [_feature(500), _feature(600)],
        "links": [],
    }))
    from grundstuecksfinder.lika_client import fetch_flurstuecke

    result = fetch_flurstuecke("6.87,51.08,6.89,51.10")
    assert len(result) == 2
    assert result[0]["properties"]["flaeche"] == 500


def test_fetch_paginates(mock_httpx):
    page1 = make_response({
        "type": "FeatureCollection",
        "features": [_feature(100)],
        "links": [{"rel": "next", "href": "http://example.com?offset=1"}],
    })
    page2 = make_response({
        "type": "FeatureCollection",
        "features": [_feature(200)],
        "links": [],
    })
    mock_httpx([page1, page2])
    from grundstuecksfinder.lika_client import fetch_flurstuecke

    result = fetch_flurstuecke("6.87,51.08,6.89,51.10", limit=1)
    assert len(result) == 2


def test_fetch_empty_result(mock_httpx):
    mock_httpx(make_response({
        "type": "FeatureCollection",
        "features": [],
        "links": [],
    }))
    from grundstuecksfinder.lika_client import fetch_flurstuecke

    result = fetch_flurstuecke("0,0,0.001,0.001")
    assert result == []
