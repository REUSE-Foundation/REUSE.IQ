#!/usr/bin/env python3
"""
Merges data/geocoordinates.csv (a persistent slug -> Latitude/Longitude/Geocode
precision lookup) into data/REUSE_V5_Master.csv.

Run this AFTER scripts/parse_md_to_csv.py rebuilds the master CSV, and BEFORE
scripts/build_site.py / generate_locations_json.py need coordinates. Coordinates
live in geocoordinates.csv rather than the organisation .md files themselves,
since they're a derived/geocoded lookup, not researched organisational content -
this keeps them from being lost or needing to be hand-maintained across 800+
markdown files.

Usage:
    python3 scripts/merge_geocoordinates.py data/REUSE_V5_Master.csv data/geocoordinates.csv
"""
import csv
import sys


def main(master_path: str, geo_path: str) -> None:
    with open(geo_path, newline="", encoding="utf-8") as f:
        geo_lookup = {
            row["GitHub slug"].strip(): row
            for row in csv.DictReader(f)
            if row.get("GitHub slug", "").strip()
        }

    with open(master_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    for col in ("Latitude", "Longitude", "Geocode precision"):
        if col not in fieldnames:
            fieldnames.append(col)

    matched = 0
    missing = []
    for row in rows:
        slug = row.get("GitHub slug", "").strip()
        geo = geo_lookup.get(slug)
        if geo:
            row["Latitude"] = geo.get("Latitude", "")
            row["Longitude"] = geo.get("Longitude", "")
            row["Geocode precision"] = geo.get("Geocode precision", "")
            matched += 1
        else:
            row.setdefault("Latitude", "")
            row.setdefault("Longitude", "")
            row.setdefault("Geocode precision", "")
            missing.append(row.get("Organisation", slug))

    with open(master_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Merged coordinates for {matched} of {len(rows)} organisations.")
    if missing:
        print(f"{len(missing)} organisation(s) have NO coordinates yet (need geocoding):")
        for name in missing:
            print(f"  - {name}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
