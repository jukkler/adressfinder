"""Streamlit GUI for Grundstücksfinder NRW."""

from __future__ import annotations

import csv
import io
from math import cos, radians

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from grundstuecksfinder.filter import filter_by_area, filter_by_nutzung
from grundstuecksfinder.geocoder import geocode
from grundstuecksfinder.lika_client import fetch_flurstuecke, fetch_gebaeude
from grundstuecksfinder.map_builder import build_map

# ---------------------------------------------------------------------------
# Page config — must be the FIRST Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Grundstücksfinder NRW", layout="wide")

# ---------------------------------------------------------------------------
# Session-state defaults
# ---------------------------------------------------------------------------
_STATE_DEFAULTS: dict = {
    "matches": [],
    "gebaeude": [],
    "bbox": None,
    "center_lat": 51.5,
    "center_lon": 7.0,
    "search_summary": "",
}

for key, default in _STATE_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def matches_to_csv_bytes(matches: list[dict]) -> bytes:
    """Serialise match dicts to UTF-8 CSV bytes for download."""
    output = io.StringIO()
    fieldnames = [
        "adresse",
        "flaeche",
        "abweichung",
        "gemeinde",
        "kreis",
        "flstkennz",
        "nutzung",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(matches)
    return output.getvalue().encode("utf-8")


def _bbox_from_point(lat: float, lon: float, radius: float) -> str:
    """Compute a bounding-box string from a centre point and radius in metres."""
    delta_lat = radius / 111_000
    delta_lon = radius / (111_000 * cos(radians(lat)))
    return f"{lon - delta_lon},{lat - delta_lat},{lon + delta_lon},{lat + delta_lat}"


# ---------------------------------------------------------------------------
# Sidebar — search parameters & layer controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("Grundstücksfinder NRW")

    # -- Search mode ---------------------------------------------------------
    search_mode = st.radio(
        "Suchmodus",
        ["Textsuche", "Kartenklick", "Zeichnen"],
        horizontal=True,
    )

    # -- Conditional inputs per mode -----------------------------------------
    ort = ""
    radius: float | None = None

    if search_mode == "Textsuche":
        ort = st.text_input("Ort / Adresse", placeholder="z.\u202fB. Köln Ehrenfeld")
        radius = st.number_input(
            "Radius (m)",
            min_value=0,
            value=0,
            step=100,
            help="Optional — wird kein Radius angegeben, wird die Nominatim-Bounding-Box genutzt.",
        )
        if radius == 0:
            radius = None
    elif search_mode == "Kartenklick":
        radius = st.number_input(
            "Radius (m)",
            min_value=100,
            value=500,
            step=100,
        )
        st.info("Klicken Sie auf die Karte, um den Suchbereich festzulegen.")
    else:  # Zeichnen
        st.info("Zeichnen Sie ein Rechteck auf der Karte, um den Suchbereich festzulegen.")

    # -- Always-visible inputs -----------------------------------------------
    flaeche = st.number_input(
        "Fläche (m²)",
        min_value=1,
        value=500,
        step=50,
    )
    toleranz = st.slider("Toleranz (%)", min_value=1, max_value=30, value=10)
    nutzung = st.text_input("Nutzung (optional)", placeholder="z.\u202fB. Wohnbaufläche")

    # -- Search button -------------------------------------------------------
    search_clicked = st.button("Suchen", type="primary", use_container_width=True)

    st.divider()

    # -- Layer toggles -------------------------------------------------------
    show_flurstuecke = st.checkbox("Flurstücke", value=True)
    show_gebaeude_layer = st.checkbox("Gebäude", value=False)
    show_bbox_layer = st.checkbox("Suchbereich", value=True)

    tile_layer = st.selectbox(
        "Basiskarte",
        ["OpenStreetMap", "Esri.WorldImagery", "OpenTopoMap"],
    )


# ---------------------------------------------------------------------------
# Search logic
# ---------------------------------------------------------------------------
def _run_search(
    bbox: str,
    lat: float,
    lon: float,
    summary: str,
) -> None:
    """Execute the search pipeline and store results in session state."""
    features = fetch_flurstuecke(bbox)
    matches = filter_by_area(features, flaeche, toleranz)
    if nutzung:
        matches = filter_by_nutzung(matches, nutzung)

    geb: list[dict] = []
    if show_gebaeude_layer:
        geb = fetch_gebaeude(bbox)

    st.session_state["matches"] = matches
    st.session_state["gebaeude"] = geb
    st.session_state["bbox"] = bbox
    st.session_state["center_lat"] = lat
    st.session_state["center_lon"] = lon
    st.session_state["search_summary"] = summary


if search_clicked:
    if search_mode == "Textsuche":
        if not ort:
            st.error("Bitte geben Sie einen Ort ein.")
        else:
            with st.spinner("Suche läuft..."):
                try:
                    geo = geocode(ort, radius)
                except ValueError as exc:
                    st.error(str(exc))
                    geo = None

                if geo is not None:
                    summary = f"Textsuche: {ort}"
                    if radius:
                        summary += f" ({radius:.0f}\u202fm)"
                    _run_search(geo["bbox"], geo["lat"], geo["lon"], summary)

    elif search_mode == "Kartenklick":
        lc = st.session_state.get("_last_clicked")
        if lc is None:
            st.error("Bitte klicken Sie zuerst auf die Karte.")
        else:
            lat, lon = lc["lat"], lc["lng"]
            with st.spinner("Suche läuft..."):
                bbox = _bbox_from_point(lat, lon, radius)
                summary = f"Kartenklick: {lat:.5f}, {lon:.5f} ({radius:.0f}\u202fm)"
                _run_search(bbox, lat, lon, summary)

    elif search_mode == "Zeichnen":
        drawing = st.session_state.get("_last_drawing")
        if drawing is None:
            st.error("Bitte zeichnen Sie zuerst ein Rechteck auf der Karte.")
        else:
            with st.spinner("Suche läuft..."):
                coords = drawing["geometry"]["coordinates"][0]
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                min_lon, max_lon = min(lons), max(lons)
                min_lat, max_lat = min(lats), max(lats)
                bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"
                center_lat = (min_lat + max_lat) / 2
                center_lon = (min_lon + max_lon) / 2
                summary = "Zeichnen (Rechteck auf Karte)"
                _run_search(bbox, center_lat, center_lon, summary)


# ---------------------------------------------------------------------------
# Main area — status bar
# ---------------------------------------------------------------------------
matches: list[dict] = st.session_state["matches"]

col_treffer, col_summary, col_download = st.columns([1, 3, 1])

with col_treffer:
    st.metric("Treffer", len(matches))

with col_summary:
    if st.session_state["search_summary"]:
        st.markdown(f"**{st.session_state['search_summary']}**")

with col_download:
    if matches:
        st.download_button(
            label="CSV herunterladen",
            data=matches_to_csv_bytes(matches),
            file_name="grundstuecke.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ---------------------------------------------------------------------------
# Main area — results table
# ---------------------------------------------------------------------------
selected_idx: int | None = None

if matches:
    display_data = [
        {
            "Adresse": m["adresse"],
            "Fläche (m²)": m["flaeche"],
            "Abweichung (%)": m["abweichung"],
            "Gemeinde": m["gemeinde"],
            "Kreis": m["kreis"],
            "Flurstückskennz.": m["flstkennz"],
            "Nutzung": m["nutzung"],
        }
        for m in matches
    ]
    df = pd.DataFrame(display_data)

    event = st.dataframe(
        df,
        on_select="rerun",
        selection_mode="single-row",
        use_container_width=True,
    )

    selected_rows = event.selection.rows
    if selected_rows:
        selected_idx = selected_rows[0]

# ---------------------------------------------------------------------------
# Main area — interactive map
# ---------------------------------------------------------------------------
enable_draw = search_mode == "Zeichnen"

m = build_map(
    center_lat=st.session_state["center_lat"],
    center_lon=st.session_state["center_lon"],
    zoom=13,
    matches=matches if show_flurstuecke else None,
    gebaeude=st.session_state["gebaeude"] if show_gebaeude_layer else None,
    bbox=st.session_state["bbox"] if show_bbox_layer else None,
    selected_idx=selected_idx,
    show_flurstuecke=show_flurstuecke,
    show_gebaeude=show_gebaeude_layer,
    show_bbox=show_bbox_layer,
    tile_layer=tile_layer,
    enable_draw=enable_draw,
)

map_data = st_folium(
    m,
    width=None,
    height=500,
    returned_objects=["last_clicked", "last_active_drawing"],
)

# Capture map interactions for Kartenklick / Zeichnen modes
if map_data:
    if map_data.get("last_clicked") is not None:
        st.session_state["_last_clicked"] = map_data["last_clicked"]
    if map_data.get("last_active_drawing") is not None:
        st.session_state["_last_drawing"] = map_data["last_active_drawing"]
