def filter_by_area(
    features: list[dict], target_m2: float, tolerance_pct: float = 10.0
) -> list[dict]:
    """Filter GeoJSON features by area within tolerance, sorted by deviation."""
    min_area = target_m2 * (1 - tolerance_pct / 100)
    max_area = target_m2 * (1 + tolerance_pct / 100)

    matches = []
    for f in features:
        props = f.get("properties", {})
        flaeche = props.get("flaeche")
        if flaeche is None:
            continue
        if min_area <= flaeche <= max_area:
            deviation = ((flaeche - target_m2) / target_m2) * 100
            matches.append({
                "adresse": props.get("lagebeztxt") or "–",
                "flaeche": flaeche,
                "abweichung": round(deviation, 1),
                "gemeinde": props.get("gemeinde", "–"),
                "kreis": props.get("kreis", "–"),
                "flstkennz": props.get("flstkennz", "–"),
                "nutzung": props.get("tntxt") or "–",
                "geometrie": f.get("geometry"),
            })

    return sorted(matches, key=lambda x: abs(x["abweichung"]))


def filter_by_nutzung(matches: list[dict], nutzung: str) -> list[dict]:
    """Filter matches where nutzung contains the search term (case-insensitive)."""
    return [m for m in matches if nutzung.lower() in m["nutzung"].lower()]
