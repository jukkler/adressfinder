import httpx

BASE_URL = "https://ogc-api.nrw.de/lika/v1/collections/flurstueck/items"


def fetch_flurstuecke(bbox: str, limit: int = 500) -> list[dict]:
    """Fetch all Flurstücke within a bounding box, handling pagination."""
    all_features: list[dict] = []
    offset = 0

    while True:
        resp = httpx.get(
            BASE_URL,
            params={"f": "json", "bbox": bbox, "limit": limit, "offset": offset},
        )
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features", [])
        all_features.extend(features)

        has_next = any(link.get("rel") == "next" for link in data.get("links", []))
        if not has_next or len(features) < limit:
            break
        offset += limit

    return all_features
