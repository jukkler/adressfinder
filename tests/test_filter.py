from grundstuecksfinder.filter import filter_by_area, filter_by_nutzung


def _feature(flaeche, lagebeztxt="Teststraße 1", tntxt="Wohnbaufläche;500"):
    return {
        "type": "Feature",
        "properties": {
            "flaeche": flaeche,
            "lagebeztxt": lagebeztxt,
            "gemeinde": "Teststadt",
            "kreis": "Testkreis",
            "flstkennz": "05111000100001______",
            "tntxt": tntxt,
        },
        "geometry": {"type": "MultiPolygon", "coordinates": []},
    }


def test_filter_exact_match():
    result = filter_by_area([_feature(500)], target_m2=500, tolerance_pct=10)
    assert len(result) == 1
    assert result[0]["flaeche"] == 500
    assert result[0]["abweichung"] == 0.0


def test_filter_within_tolerance():
    features = [_feature(540), _feature(460), _feature(700)]
    result = filter_by_area(features, target_m2=500, tolerance_pct=10)
    # 540 (+8%) and 460 (-8%) match; 700 (+40%) does not
    assert len(result) == 2


def test_filter_sorted_by_deviation():
    features = [_feature(550), _feature(500), _feature(450)]
    result = filter_by_area(features, target_m2=500, tolerance_pct=15)
    assert result[0]["flaeche"] == 500  # 0% first
    assert abs(result[1]["abweichung"]) <= abs(result[2]["abweichung"])


def test_filter_skips_missing_flaeche():
    features = [{"properties": {}, "geometry": None}]
    result = filter_by_area(features, target_m2=500, tolerance_pct=10)
    assert result == []


def test_filter_by_nutzung():
    matches = [
        {"nutzung": "Wohnbaufläche;500", "adresse": "A"},
        {"nutzung": "Gewerbe;300", "adresse": "B"},
    ]
    result = filter_by_nutzung(matches, "Wohnbau")
    assert len(result) == 1
    assert result[0]["adresse"] == "A"
