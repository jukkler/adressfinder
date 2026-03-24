import csv
from tabulate import tabulate


def _clean_nutzung(tntxt: str) -> str:
    """Extract human-readable nutzung from tntxt format 'Nutzung;Fläche|Nutzung;Fläche'."""
    if not tntxt or tntxt == "–":
        return "–"
    parts = tntxt.split("|")
    return ", ".join(p.split(";")[0].strip() for p in parts)


def format_table(matches: list[dict]) -> str:
    """Format matches as a tabulated string for terminal output."""
    if not matches:
        return "Keine Treffer gefunden."

    rows = []
    for i, m in enumerate(matches, 1):
        sign = "+" if m["abweichung"] > 0 else ""
        rows.append([
            i,
            m["adresse"],
            f"{m['flaeche']:.0f} m²",
            f"{sign}{m['abweichung']}%",
            _clean_nutzung(m["nutzung"]),
            m["flstkennz"],
        ])

    headers = ["#", "Adresse", "Fläche", "Abw.", "Nutzung", "Flurstückskennz."]
    return tabulate(rows, headers=headers, tablefmt="simple")


def export_csv(matches: list[dict], filepath: str) -> None:
    """Export matches to a CSV file."""
    fieldnames = ["adresse", "flaeche", "abweichung", "gemeinde", "kreis", "flstkennz", "nutzung"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(matches)
