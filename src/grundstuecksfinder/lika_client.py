import httpx

_BASE = "https://ogc-api.nrw.de/lika/v1/collections"


def _fetch_collection(collection: str, bbox: str, limit: int = 500) -> list[dict]:
    """Fetch all features from a LIKA collection, handling pagination."""
    url = f"{_BASE}/{collection}/items"
    all_features: list[dict] = []
    offset = 0

    while True:
        resp = httpx.get(url, params={"f": "json", "bbox": bbox, "limit": limit, "offset": offset})
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features", [])
        all_features.extend(features)

        has_next = any(link.get("rel") == "next" for link in data.get("links", []))
        if not has_next or len(features) < limit:
            break
        offset += limit

    return all_features


def fetch_flurstuecke(bbox: str, limit: int = 500) -> list[dict]:
    """Fetch all Flurstücke within a bounding box."""
    return _fetch_collection("flurstueck", bbox, limit)


def fetch_gebaeude(bbox: str, limit: int = 500) -> list[dict]:
    """Fetch all Gebäude/Bauwerke within a bounding box."""
    return _fetch_collection("gebaeude_bauwerk", bbox, limit)
