import click
from grundstuecksfinder.geocoder import geocode
from grundstuecksfinder.lika_client import fetch_flurstuecke
from grundstuecksfinder.filter import filter_by_area, filter_by_nutzung
from grundstuecksfinder.formatter import format_table, export_csv


@click.command()
@click.argument("ort")
@click.option("-f", "--flaeche", required=True, type=float, help="Ziel-Grundstücksgröße in m²")
@click.option("-t", "--toleranz", default=10.0, type=float, help="Toleranz in Prozent")
@click.option("--radius", default=None, type=float, help="Suchradius in Metern (überschreibt BBox)")
@click.option("--nutzung", default=None, type=str, help="Filter auf Nutzungsart")
@click.option("--limit", default=500, type=int, help="Max. Flurstücke pro API-Seite")
@click.option("--karte", is_flag=True, help="HTML-Karte generieren")
@click.option("--csv", "csv_path", default=None, type=str, help="Ergebnisse als CSV speichern")
def main(ort, flaeche, toleranz, radius, nutzung, limit, karte, csv_path):
    """Grundstücksfinder NRW - Flurstücke nach Ort und Fläche suchen."""
    min_area = flaeche * (1 - toleranz / 100)
    max_area = flaeche * (1 + toleranz / 100)
    click.echo(f"Suche: {ort} | Fläche: {flaeche:.0f} m² ± {toleranz:.0f}% ({min_area:.0f}–{max_area:.0f} m²)")

    geo = geocode(ort, radius_m=radius)
    click.echo(f"Geocoded BBox: [{geo['bbox']}]")

    features = fetch_flurstuecke(geo["bbox"], limit=limit)
    click.echo(f"API-Abfrage: {len(features)} Flurstücke geladen")

    matches = filter_by_area(features, flaeche, toleranz)
    if nutzung:
        matches = filter_by_nutzung(matches, nutzung)

    click.echo()
    click.echo(format_table(matches))
    click.echo(f"\n{len(matches)} Treffer gefunden.")

    if csv_path:
        export_csv(matches, csv_path)
        click.echo(f"CSV gespeichert: {csv_path}")

    if karte:
        from grundstuecksfinder.map_export import export_map
        map_path = "ergebnis_karte.html"
        export_map(matches, geo["lat"], geo["lon"], map_path)
        click.echo(f"Karte: ./{map_path}")
