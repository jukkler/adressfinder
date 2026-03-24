# GUI für Grundstücksfinder NRW — Design Spec

## Context

Die CLI-App (8 Module, 21 Tests) ist fertig. Der User möchte eine grafische Oberfläche mit Streamlit, die alle CLI-Features plus erweiterte Karteninteraktivität bietet.

## Design

### Tech Stack
- **Streamlit** — Web-UI Framework
- **streamlit-folium** — Folium-Kartenintegration in Streamlit
- **folium.plugins.Draw** — Zeichentool auf der Karte

### Layout: Sidebar + Hauptbereich

**Sidebar:**
- Suchmodus-Toggle: Textsuche / Kartenklick / Zeichnen
- Eingabefelder: Ort, Fläche (m²), Toleranz (Slider 1-30%), Radius (optional), Nutzung (optional)
- Suchen-Button
- Layer-Steuerung: Flurstücke (blau), Gebäude (orange), Suchbereich ein/aus
- Basiskarte: Straße / Satellit / Topographisch

**Hauptbereich oben — Statusleiste:**
- Treffer-Anzahl, Suchparameter-Zusammenfassung, CSV-Download-Button

**Hauptbereich mitte — Ergebnistabelle:**
- Sortierbar nach Spalten
- Zeile anklickbar → hebt Polygon auf Karte hervor (rot)
- Spalten: Adresse, Fläche, Abweichung, Nutzung, Gemeinde

**Hauptbereich unten — Interaktive Karte:**
- Flurstück-Polygone (blau) mit Popups (Adresse, Fläche)
- Gebäude-Polygone (orange) mit Popups (Funktion, Baujahr)
- Suchbereich als gestricheltes Rechteck
- Ausgewähltes Flurstück rot hervorgehoben
- Zeichentool für manuelle BBox
- Klick-Suche: Klick setzt Suchpunkt
- Legende

### 3 Suchmodi
1. **Textsuche** — Ort eingeben → Nominatim → BBox (wie CLI)
2. **Kartenklick** — Klick auf Karte setzt Zentrum, Radius ergibt BBox
3. **Zeichnen** — Rechteck auf Karte zeichnen = direkte BBox

### Gebäude-Overlay
- Neuer API-Call: `GET /lika/v1/collections/gebaeude_bauwerk/items?f=json&bbox=...`
- Separate Funktion in `lika_client.py`: `fetch_gebaeude(bbox, limit)`
- Gebäude-Properties: Funktion, Baujahr, Lagebezeichnung
- Orangene Polygone, eigener Toggle

### Datenfluss
```
Suchmodus → bbox ermitteln
  ├─ Textsuche: geocoder.geocode(ort) → bbox
  ├─ Kartenklick: click_coords + radius → bbox berechnen
  └─ Zeichnen: draw_coords → bbox direkt

bbox → lika_client.fetch_flurstuecke(bbox) → features
bbox → lika_client.fetch_gebaeude(bbox) → gebaeude (parallel)

features → filter.filter_by_area() → matches
matches → Tabelle (st.dataframe) + Karte (st_folium)
gebaeude → Karte (orangener Layer)
```

### Neue/geänderte Dateien
| Datei | Änderung |
|---|---|
| `src/grundstuecksfinder/app.py` | **Neu** — Streamlit-App (Hauptdatei) |
| `src/grundstuecksfinder/map_builder.py` | **Neu** — Baut Folium-Karte mit allen Layern |
| `src/grundstuecksfinder/lika_client.py` | **Erweitern** — `fetch_gebaeude()` hinzufügen |
| `pyproject.toml` | **Erweitern** — streamlit, streamlit-folium Dependencies |
| `tests/test_lika_client.py` | **Erweitern** — Tests für `fetch_gebaeude()` |
| `tests/test_map_builder.py` | **Neu** — Tests für Karten-Baulogik |

### Wiederverwendung bestehender Module
- `geocoder.geocode()` — für Textsuche
- `lika_client.fetch_flurstuecke()` — für Flurstück-Abfrage
- `filter.filter_by_area()` / `filter_by_nutzung()` — für Filterung
- `formatter.export_csv()` — für CSV-Download (als Bytes)

### Starten
```bash
streamlit run src/grundstuecksfinder/app.py
```
