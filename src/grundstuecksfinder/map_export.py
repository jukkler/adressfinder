import folium


def export_map(
    matches: list[dict], center_lat: float, center_lon: float, filepath: str
) -> None:
    """Export matches as an interactive HTML map with Flurstück polygons."""
    m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

    for match in matches:
        geom = match.get("geometrie")
        if not geom:
            continue
        if geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                # GeoJSON = [lon, lat], folium needs [lat, lon]
                coords = [[lat, lon] for lon, lat in polygon[0]]
                folium.Polygon(
                    locations=coords,
                    popup=f"{match['adresse']}<br>{match['flaeche']:.0f} m²",
                    color="blue",
                    fill=True,
                    fill_opacity=0.3,
                ).add_to(m)

    m.save(filepath)
