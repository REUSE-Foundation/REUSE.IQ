# Handover Notes

## What this is
A researched database of 708 circular economy / reuse / refill organisations worldwide, published as a browsable website. Research is complete (708/708).

## Where everything lives
- **GitHub repo:** `Martydell/REUSE-Foundation-Knowledge-Library` — the source of truth for all data and the site.
- **Live site:** GitHub Pages, built from the `docs/` folder in this repo.
- **Editable copy of the data:** [Google Sheet](https://docs.google.com/spreadsheets/d/10EWS_WGISunCgl024rDBcaqai4Qh6yJalAJP7zd5Sy8/edit) — a simplified 10-column export for browsing/editing outside GitHub.

## How the data flows
```
organisations/*.md  (one file per org, the real source data)
        ↓  scripts/parse_md_to_csv.py
data/REUSE_V5_Master.csv  (full 34-column dataset)
        ↓  scripts/build_site.py
docs/  (the live website)
```
To change something permanently: edit the relevant file in `organisations/`, then re-run the two scripts above to regenerate the CSV and the site, then commit and push.

## Two things to know before touching this
1. **The ★ priority rating (Essential/High/Medium/Low) is a judgment call**, made by claude for each org during its research — not a formula. Don't try to reverse-engineer or "correct" it against other fields; it just reflects the researcher's read on relevance at the time.
2. **The Google Sheet is one-way.** Editing it does *not* update the website. To make an edit stick, it needs to go back into `organisations/*.md` (or `data/REUSE_V5_Master.csv`) and get rebuilt.

## Still open / unresolved
- **Hosting on reusefoundation.org**: not yet decided. Depends on whether whoever manages that Wix site has DNS access — options range from a simple link, to a subdomain, to an embed, to a full rebuild inside Wix.
- **Sheet ↔ site sync**: currently manual/one-way. If ongoing non-technical editing becomes a priority, worth considering a proper synced data layer (e.g. Airtable) instead of the current CSV/Sheet split.

## Access needed to continue this
- GitHub collaborator access on this repo (or a repo transfer to a Reuse Foundation GitHub org).
- Edit access on the Google Sheet (share by email).
