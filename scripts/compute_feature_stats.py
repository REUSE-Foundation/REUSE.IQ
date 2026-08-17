"""Computes frequency statistics (tags, ownership, country, technology signals, partnerships,
etc.) across the full REUSE_V5_Master.csv dataset — the evidence base behind
analysis/feature_analysis.json. Free to re-run as the dataset grows; prints to stdout only,
does not write any file. Re-run this periodically (per the Feature Analysis prompt's own
usage instructions) and update analysis/feature_analysis.json by hand if the patterns shift."""

import csv
import os
import re
from collections import Counter, defaultdict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(REPO_ROOT, "data", "REUSE_V5_Master.csv")

with open(CSV_PATH, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

N = len(rows)
print(f"Total orgs: {N}\n")

def normalize_country(raw):
    c = (raw or "").strip()
    c = re.split(r"\s+[—–-]\s+", c, maxsplit=1)[0]
    c = re.sub(r"\s*\(.*$", "", c).strip()
    return c

# ---------- 1. Tags (circular economy activities) ----------
tag_counter = Counter()
for r in rows:
    tags = [t.strip() for t in r["Tags"].split(",") if t.strip() and t.strip() != "Not publicly available"]
    tag_counter.update(tags)
print("=== TAG FREQUENCY (Circular Economy Activities) ===")
for tag, n in tag_counter.most_common(20):
    print(f"{n:4d} ({n/N*100:5.1f}%)  {tag}")

# ---------- 2. Ownership status ----------
def normalize_ownership(raw):
    r = (raw or "").strip().lower()
    if not r or r == "not publicly available":
        return "Unknown"
    if "non-profit" in r or "nonprofit" in r or "ngo" in r or "charity" in r or "cooperative" in r or "co-operative" in r:
        return "Non-profit / NGO / Cooperative"
    if "subsidiary" in r or "brand" in r and "unilever" in r:
        return "Subsidiary of larger company"
    if "public listed" in r or "publicly listed" in r or "nasdaq" in r or "nyse" in r or "lse" in r:
        return "Public listed"
    if "venture" in r or "vc-backed" in r or "vc backed" in r:
        return "Private, venture-backed"
    if "family" in r:
        return "Private, family-owned"
    if "social enterprise" in r:
        return "Private social enterprise"
    if "government" in r or "public/government" in r or "municipal" in r or "state" in r:
        return "Government / public sector"
    if "private" in r:
        return "Private (independent)"
    return "Other"

own_counter = Counter(normalize_ownership(r["Ownership status"]) for r in rows)
print("\n=== OWNERSHIP STATUS ===")
for k, n in own_counter.most_common():
    print(f"{n:4d} ({n/N*100:5.1f}%)  {k}")

# ---------- 3. Country ----------
country_counter = Counter(normalize_country(r["Country"]) for r in rows)
print(f"\n=== COUNTRY (top 20 of {len(country_counter)} unique) ===")
for c, n in country_counter.most_common(20):
    print(f"{n:4d} ({n/N*100:5.1f}%)  {c}")

# ---------- 4. Priority rating ----------
def priority_bucket(raw):
    r = raw or ""
    if "Essential" in r: return "Essential"
    if "High" in r: return "High"
    if "Medium" in r: return "Medium"
    if "Low relevance" in r: return "Low relevance"
    if "Low" in r: return "Low"
    return "Unrated"

priority_counter = Counter(priority_bucket(r["REUSE priority rating"]) for r in rows)
print("\n=== PRIORITY RATING ===")
for k in ["Essential", "High", "Medium", "Low", "Low relevance", "Unrated"]:
    n = priority_counter.get(k, 0)
    print(f"{n:4d} ({n/N*100:5.1f}%)  {k}")

# ---------- 5. Status ----------
def normalize_status(raw):
    r = (raw or "").strip().lower()
    if not r: return "Unknown"
    if "inactive" in r or "closed" in r or "defunct" in r or "ceased" in r or "dormant" in r: return "Inactive/Closed"
    if "uncertain" in r or "unclear" in r or "unverified" in r: return "Uncertain"
    if "active" in r or "operating" in r: return "Active"
    return "Other: " + r[:30]

status_counter = Counter(normalize_status(r["Status"]) for r in rows)
print("\n=== STATUS ===")
for k, n in status_counter.most_common():
    print(f"{n:4d} ({n/N*100:5.1f}%)  {k}")

# ---------- 6. Company size ----------
def normalize_size(raw):
    r = (raw or "").strip()
    if not r or r.lower() == "not publicly available": return "Not disclosed"
    if re.search(r"\b1-10\b|\bsolo\b|\bfounder\b|small team", r, re.I): return "Micro (1-10)"
    if re.search(r"\b11-50\b|\b10-50\b", r, re.I): return "Small (11-50)"
    if re.search(r"\b51-200\b|\b50-200\b", r, re.I): return "Medium (51-200)"
    if re.search(r"\b200\+|\b500\+|\b1,000\+|\b1000\+|thousand", r, re.I): return "Large (200+)"
    return "Other/Mixed"

size_counter = Counter(normalize_size(r["Est. company size"]) for r in rows)
print("\n=== COMPANY SIZE (rough buckets) ===")
for k, n in size_counter.most_common():
    print(f"{n:4d} ({n/N*100:5.1f}%)  {k}")

# ---------- 7. Technology / infrastructure keyword scan ----------
tech_keywords = {
    "App / mobile app": r"\bapp\b|mobile app|smartphone app",
    "QR code": r"QR[\s-]?code",
    "RFID": r"\bRFID\b",
    "Digital tracking / IoT platform": r"\btrack(ing|s)?\b.{0,20}(digital|platform|technolog)|IoT|smart (bin|dispenser|kiosk|station)",
    "Deposit system": r"\bdeposit\b",
    "Subscription model": r"\bsubscription\b",
    "Franchise model": r"\bfranchise\b",
    "Vending machine / kiosk": r"vending machine|\bkiosk\b",
    "AI / machine learning": r"\bAI\b|artificial intelligence|machine learning|dynamic pricing",
    "Blockchain": r"blockchain",
    "Washing / sanitisation infrastructure": r"wash(ing)?|sanitis|sterilis",
}
core_text_fields = lambda r: " ".join([r.get("Core model", ""), r.get("Short summary", ""), r.get("Categories", "")])
tech_counter = {}
tech_examples = defaultdict(list)
for label, pattern in tech_keywords.items():
    matches = [r["Organisation"] for r in rows if re.search(pattern, core_text_fields(r), re.I)]
    tech_counter[label] = len(matches)
    tech_examples[label] = matches[:6]

print("\n=== TECHNOLOGY / INFRASTRUCTURE SIGNALS ===")
for label, n in sorted(tech_counter.items(), key=lambda x: -x[1]):
    print(f"{n:4d} ({n/N*100:5.1f}%)  {label}  e.g. {tech_examples[label][:4]}")

# ---------- 8. Customer segment keyword scan ----------
customer_keywords = {
    "B2C direct consumer": r"\bB2C\b|direct.to.consumer|consumers?\b",
    "B2B (business/retail)": r"\bB2B\b|retailers?|supermarkets?|businesses",
    "B2B2C (platform connecting both)": r"\bB2B2C\b",
    "Restaurants/hospitality/food delivery": r"restaurant|caf[eé]|hospitality|takeaway|food delivery|catering",
    "Events/festivals": r"\bevents?\b|festival",
    "Workplace/office": r"workplace|office\b|canteen",
    "Government/municipal": r"municipal|government|city council|public sector",
}
cust_counter = {}
for label, pattern in customer_keywords.items():
    matches = [r["Organisation"] for r in rows if re.search(pattern, r.get("Primary customers", "") + " " + core_text_fields(r), re.I)]
    cust_counter[label] = len(matches)

print("\n=== CUSTOMER SEGMENT SIGNALS ===")
for label, n in sorted(cust_counter.items(), key=lambda x: -x[1]):
    print(f"{n:4d} ({n/N*100:5.1f}%)  {label}")

# ---------- 9. Partnership ecosystem - frequently named corporate partners ----------
partner_text = " ".join(r.get("Key partners / customers", "") for r in rows)
known_corps = ["Unilever", "Coca-Cola", "Carrefour", "Walmart", "Tesco", "Nestle", "Nestlé", "IKEA", "Uber Eats",
               "Marks & Spencer", "Sainsbury", "Waitrose", "Auchan", "Aldi", "Monoprix", "P&G", "Danone",
               "Coop", "Migros", "Costco", "Target", "Ocado", "Amazon"]
partner_counter = Counter()
for corp in known_corps:
    n = len(re.findall(re.escape(corp), partner_text, re.I))
    if n:
        partner_counter[corp] = n
print("\n=== NAMED CORPORATE PARTNERS/RETAILERS (mentions across dataset) ===")
for corp, n in partner_counter.most_common(20):
    print(f"{n:4d}  {corp}")

# ---------- 10. SDGs ----------
sdg_counter = Counter()
for r in rows:
    sdgs = [s.strip() for s in r["SDGs"].split(";") if s.strip()]
    sdg_counter.update(sdgs)
print("\n=== SDG FREQUENCY ===")
for k, n in sdg_counter.most_common(10):
    print(f"{n:4d} ({n/N*100:5.1f}%)  {k}")

# ---------- 11. Confidence ----------
conf_counter = Counter(r["Overall confidence"].strip() for r in rows)
print("\n=== OVERALL CONFIDENCE ===")
for k, n in conf_counter.most_common():
    print(f"{n:4d} ({n/N*100:5.1f}%)  {k}")

# ---------- 12. Cross-tab: Essential/High priority orgs -> what tags dominate ----------
top_orgs = [r for r in rows if priority_bucket(r["REUSE priority rating"]) in ("Essential", "High")]
top_tag_counter = Counter()
for r in top_orgs:
    tags = [t.strip() for t in r["Tags"].split(",") if t.strip() and t.strip() != "Not publicly available"]
    top_tag_counter.update(tags)
print(f"\n=== TAGS AMONG ESSENTIAL/HIGH PRIORITY ORGS (n={len(top_orgs)}) ===")
for tag, n in top_tag_counter.most_common(10):
    print(f"{n:4d} ({n/len(top_orgs)*100:5.1f}%)  {tag}")

# ---------- 13. Examples for write-up: pull a few concrete named orgs per key pattern ----------
def sample_examples(pattern_field_fn, pattern, k=5):
    matches = [r["Organisation"] for r in rows if re.search(pattern, pattern_field_fn(r), re.I)]
    return matches[:k]

print("\n=== SAMPLE EXAMPLES FOR WRITE-UP ===")
print("Deposit-return system orgs:", sample_examples(core_text_fields, r"\bdeposit\b", 8))
print("App/RFID-tracked reuse orgs:", sample_examples(core_text_fields, r"\bapp\b.{0,30}(track|RFID|QR)|RFID.{0,30}app", 8))
print("Subscription-model orgs:", sample_examples(core_text_fields, r"\bsubscription\b", 8))
print("Franchise-model orgs:", sample_examples(core_text_fields, r"\bfranchise\b", 8))
print("Non-profit/NGO orgs (sample):", [r["Organisation"] for r in rows if normalize_ownership(r["Ownership status"]) == "Non-profit / NGO / Cooperative"][:10])
print("Subsidiary of major FMCG (sample):", [r["Organisation"] for r in rows if "unilever" in r.get("Ownership status","").lower() or "unilever" in r.get("Organisation","").lower()][:10])
