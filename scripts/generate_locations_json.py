#!/usr/bin/env python3
"""
Regenerates reuse_locations.json from REUSE_V5_Master.csv.

Run this as part of the same build step that already rebuilds the
REUSE-IQ table/card view, so the map data never drifts out of sync
with the main CSV.

Usage:
    python3 generate_locations_json.py REUSE_V5_Master.csv data/reuse_locations.json
"""
import csv
import json
import re
import sys


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def shorten(text: str, max_len: int = 60) -> str:
    text = text.split("(")[0].split("—")[0].split(",")[0].strip()
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def status_bucket(status: str) -> str:
    s = status.lower()
    if "uncertain" in s:
        return "uncertain"
    if "acquired" in s:
        return "acquired"
    return "active"


def main(csv_path: str, out_path: str) -> None:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    idx = {h: i for i, h in enumerate(header)}
    required = ["Organisation", "Country", "Categories", "Status", "Latitude", "Longitude"]
    missing = [c for c in required if c not in idx]
    if missing:
        sys.exit(f"CSV is missing required column(s): {missing}")

    records = []
    skipped = 0
    for row in rows:
        lat, lon = row[idx["Latitude"]], row[idx["Longitude"]]
        if not lat or not lon:
            skipped += 1
            continue

        name = row[idx["Organisation"]]
        precision_raw = row[idx["Geocode precision"]] if "Geocode precision" in idx else ""
        precision = "city" if precision_raw in ("city", "city (manual)") else "country"

        records.append(
            {
                "id": slugify(name),
                "name": name,
                "lat": round(float(lat), 4),
                "lon": round(float(lon), 4),
                "country": shorten(row[idx["Country"]]),
                "category": shorten(row[idx["Categories"]]),
                "precision": precision,
                "status": status_bucket(row[idx["Status"]]),
            }
        )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Wrote {len(records)} records to {out_path} ({skipped} rows skipped, no coordinates).")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
