# tests/test_map_builder.py
from grundstuecksfinder.map_builder import build_map


def _match(adresse="Teststr. 1", flaeche=500, abweichung=0.0):
    return {
        "adresse": adresse,
        "flaeche": flaeche,
        "abweichung": abweichung,
        "geometrie": {
            "type": "MultiPolygon",
            "coordinates": [[[[6.87, 51.08], [6.88, 51.08], [6.88, 51.09], [6.87, 51.09], [6.87, 51.08]]]],
        },
    }


def _gebaeude(funktion="Wohngebäude"):
    return {
        "properties": {"funktion": funktion},
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[[[6.875, 51.085], [6.876, 51.085], [6.876, 51.086], [6.875, 51.085]]]],
        },
    }


def test_build_empty_map():
    m = build_map()
    html = m._repr_html_()
    assert "leaflet" in html.lower()


def test_build_map_with_matches():
    m = build_map(matches=[_match(), _match(adresse="Str. 2")], show_flurstuecke=True)
    html = m._repr_html_()
    assert "Teststr. 1" in html
    assert "Str. 2" in html


def test_build_map_with_selected():
    m = build_map(matches=[_match(), _match(adresse="Selected")], selected_idx=1)
    html = m._repr_html_()
    assert "Selected" in html
    # Selected polygon should use red color
    assert "#ff4b4b" in html


def test_build_map_with_gebaeude():
    m = build_map(gebaeude=[_gebaeude()], show_gebaeude=True)
    html = m._repr_html_()
    assert "Wohngebäude" in html.lower() or "wohngeb" in html.lower()
    assert "#f7a04a" in html


def test_build_map_with_bbox():
    m = build_map(bbox="6.87,51.08,6.89,51.10", show_bbox=True)
    html = m._repr_html_()
    assert "4a6cf7" in html


def test_build_map_with_draw():
    m = build_map(enable_draw=True)
    html = m._repr_html_()
    assert "draw" in html.lower()


def test_build_map_layers_disabled():
    m = build_map(
        matches=[_match()],
        gebaeude=[_gebaeude()],
        bbox="6.87,51.08,6.89,51.10",
        show_flurstuecke=False,
        show_gebaeude=False,
        show_bbox=False,
    )
    html = m._repr_html_()
    # Should not contain polygon-specific content when layers disabled
    assert "Teststr. 1" not in html
