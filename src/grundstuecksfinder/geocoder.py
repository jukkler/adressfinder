from math import cos, radians

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode(ort: str, radius_m: float | None = None) -> dict:
    """Geocode a location string to a bounding box and center point."""
    resp = httpx.get(
        NOMINATIM_URL,
        params={"q": ort, "format": "json", "countrycodes": "de", "limit": 1},
        headers={"User-Agent": "Grundstuecksfinder/1.0"},
    )
    resp.raise_for_status()
    results = resp.json()

    if not results:
        raise ValueError(f"Keine Ergebnisse für '{ort}'")

    result = results[0]
    lat = float(result["lat"])
    lon = float(result["lon"])

    if radius_m is not None:
        delta_lat = radius_m / 111_000
        delta_lon = radius_m / (111_000 * cos(radians(lat)))
        bbox = f"{lon - delta_lon},{lat - delta_lat},{lon + delta_lon},{lat + delta_lat}"
    else:
        bb = result["boundingbox"]  # [süd, nord, west, ost]
        bbox = f"{bb[2]},{bb[0]},{bb[3]},{bb[1]}"

    return {"bbox": bbox, "lat": lat, "lon": lon}
