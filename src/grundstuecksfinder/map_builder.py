# src/grundstuecksfinder/map_builder.py
import folium
from folium.plugins import Draw


def build_map(
    center_lat: float = 51.2277,
    center_lon: float = 6.7735,
    zoom: int = 13,
    matches: list[dict] | None = None,
    gebaeude: list[dict] | None = None,
    bbox: str | None = None,
    selected_idx: int | None = None,
    show_flurstuecke: bool = True,
    show_gebaeude: bool = True,
    show_bbox: bool = True,
    tile_layer: str = "OpenStreetMap",
    enable_draw: bool = False,
) -> folium.Map:
    """Build a folium map with Flurstück polygons, Gebäude overlay, and controls."""
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=tile_layer)

    # Draw control for bbox drawing
    if enable_draw:
        Draw(
            draw_options={
                "polyline": False,
                "polygon": False,
                "circle": False,
                "marker": False,
                "circlemarker": False,
                "rectangle": True,
            },
            edit_options={"edit": False},
        ).add_to(m)

    # Search area bbox rectangle
    if show_bbox and bbox:
        parts = [float(x) for x in bbox.split(",")]
        min_lon, min_lat, max_lon, max_lat = parts
        folium.Rectangle(
            bounds=[[min_lat, min_lon], [max_lat, max_lon]],
            color="#4a6cf7",
            weight=2,
            dash_array="8",
            fill=False,
        ).add_to(m)

    # Flurstück polygons (blue)
    if show_flurstuecke and matches:
        for i, match in enumerate(matches):
            geom = match.get("geometrie")
            if not geom:
                continue
            is_selected = selected_idx is not None and i == selected_idx
            color = "#ff4b4b" if is_selected else "#4a6cf7"
            weight = 3 if is_selected else 1.5
            fill_opacity = 0.15 if is_selected else 0.2

            if geom["type"] == "MultiPolygon":
                for polygon in geom["coordinates"]:
                    coords = [[lat, lon] for lon, lat in polygon[0]]
                    folium.Polygon(
                        locations=coords,
                        popup=f"<b>{match['adresse']}</b><br>{match['flaeche']:.0f} m² ({'+' if match['abweichung'] > 0 else ''}{match['abweichung']}%)",
                        color=color,
                        weight=weight,
                        fill=True,
                        fill_opacity=fill_opacity,
                    ).add_to(m)

    # Gebäude polygons (orange)
    if show_gebaeude and gebaeude:
        for feat in gebaeude:
            geom = feat.get("geometry")
            if not geom:
                continue
            props = feat.get("properties", {})
            funktion = props.get("funktion", "Gebäude")

            if geom["type"] == "MultiPolygon":
                for polygon in geom["coordinates"]:
                    coords = [[lat, lon] for lon, lat in polygon[0]]
                    folium.Polygon(
                        locations=coords,
                        popup=f"<b>{funktion}</b>",
                        color="#f7a04a",
                        weight=1,
                        fill=True,
                        fill_opacity=0.25,
                    ).add_to(m)

    # Internal CSS: all containers fill iframe. JS: Leaflet invalidateSize.
    map_var = m.get_name()
    m.get_root().html.add_child(folium.Element(
        "<style>"
        "html,body{height:100%!important;margin:0!important;padding:0!important}"
        "#root,#parent,.float-child{height:100%!important}"
        "#map_div{height:100%!important;width:100%!important}"
        ".folium-map,.leaflet-container{height:100%!important;width:100%!important}"
        "</style>"
        "<script>"
        "function _refresh(){try{" + map_var + ".invalidateSize();}catch(e){}}"
        "setTimeout(_refresh,300);setTimeout(_refresh,800);setTimeout(_refresh,1500);"
        "setInterval(_refresh,3000);window.addEventListener('resize',_refresh);"
        "</script>"
    ))

    return m
