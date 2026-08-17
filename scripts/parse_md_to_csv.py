import re, os, csv, sys, glob, unicodedata

FIELDNAMES = [
"Organisation","Country","Status","Official name (+source)","Also known as","Website",
"Instagram","Est. company size","Primary customers","Year founded","Ownership status",
"Core model","Geographic scope","Categories","Key partners / customers","Impact metrics",
"Conf: name","Conf: year","Conf: impact","Verification notes",
"GitHub slug","Short summary","Logo URL","Featured image URL","SEO description",
"Primary colour","Tags","Last verified date","Last updated date","Researcher",
"Source count","Overall confidence","Overall confidence score","REUSE priority rating","SDGs"
]

def get_section(text, header, next_headers):
    pat = rf"##\s*{re.escape(header)}\s*\n(.*?)(?=\n##\s|\Z)"
    m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""

# Canonical Quick Facts key -> alternate spellings/labels seen across the two
# template styles in use (table rows vs. bullet lists), lowercased and with
# whitespace collapsed / slashes single-spaced for comparison.
QUICKFACTS_KEY_ALIASES = {
    "Official Name": ["official name"],
    "Country / HQ": ["country / hq"],
    "Year Founded": ["year founded"],
    "Status": ["status"],
    "Ownership": ["ownership", "ownership status"],
    "Website": ["website"],
    "Primary Category": ["primary category", "categories"],
    "Also known as": ["also known as"],
    "Geographic scope": ["geographic scope"],
    "REUSE priority rating": ["reuse priority rating"],
    "SDGs": ["sdgs"],
    "Est. company size": ["est. company size", "est company size"],
}
_QUICKFACTS_ALIAS_LOOKUP = {
    alias: canon for canon, aliases in QUICKFACTS_KEY_ALIASES.items() for alias in aliases
}

def _normalize_quickfacts_key(raw_key):
    key = re.sub(r"\s+", " ", raw_key).strip()
    key = re.sub(r"\s*/\s*", " / ", key)
    canon = _QUICKFACTS_ALIAS_LOOKUP.get(key.lower())
    return canon if canon else key

def parse_quickfacts(text):
    m = re.search(r"##\s*Quick Facts\s*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    facts = {}
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if line.startswith("|"):
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) == 2 and cells[0] not in ("Field", "---"):
                    facts[_normalize_quickfacts_key(cells[0])] = cells[1]
                continue
            bm = re.match(r"^-\s*\*\*(.+?)\*\*\s*:?\s*(.*)$", line)
            if bm:
                key = bm.group(1).rstrip(":").strip()
                value = bm.group(2).strip()
                if value:
                    facts[_normalize_quickfacts_key(key)] = value
    return facts

def parse_confidence_footer(text):
    m = re.search(r"Confidence\s*—\s*Name:\s*(\w+)\s*\|\s*Founding Year:\s*(\w+)\s*\|\s*Impact Data:\s*(\w+)\s*\|\s*Last Verified:\s*([\d-]+)", text)
    if m:
        return m.group(1), m.group(2), m.group(3), m.group(4)
    return "Medium","Medium","Low","2026-07-17"

def score(level):
    return {"High":100,"Medium":60,"Low":30}.get(level.strip(), 50)

def parse_priority(text):
    m = re.search(r"Priority[:\s]*([★☆]+)\s*(\w[\w\s]*)", text)
    if m:
        return f"{m.group(1)} {m.group(2).strip()}"
    m2 = re.search(r"(★{1,5})\s*(Essential|High|Medium|Low relevance|Low)", text)
    if m2:
        return f"{m2.group(1)} {m2.group(2)}"
    return "Not publicly available"

def word_slice(text, n_words):
    words = re.sub(r"\s+", " ", text).strip().split(" ")
    return " ".join(words[:n_words])

CATEGORY_TAGS = {
    "reusable packaging":"reusable-packaging","refill":"refill","deposit return":"deposit-return",
    "packaging-as-a-service":"packaging-as-a-service","repair":"repair","rental":"rental","sharing":"sharing",
    "reverse logistics":"reverse-logistics","take-back":"take-back","industrial reuse":"industrial-reuse",
    "waste reduction":"waste-reduction","consumer education":"consumer-education","digital tracking":"digital-tracking",
    "material recovery":"material-recovery"
}
SDG_MAP = [
    (["refill","reusable packaging","deposit return","material recovery","waste reduction","packaging-as-a-service"], "SDG 12: Responsible Consumption and Production"),
    (["rental","sharing","reverse logistics","take-back","industrial reuse"], "SDG 12: Responsible Consumption and Production"),
    (["consumer education"], "SDG 4: Quality Education"),
    (["climate","co2","carbon"], "SDG 13: Climate Action"),
]

def derive_tags_sdgs(activities_text, categories_field):
    # Only use actual bullet lines, not the "Not identified from public sources:" disclaimer
    bullets = "\n".join(l for l in activities_text.splitlines() if l.strip().startswith("-"))
    low = (bullets + " " + categories_field).lower()
    tags = sorted({tag for key,tag in CATEGORY_TAGS.items() if key in low})
    sdgs = []
    for keys, sdg in SDG_MAP:
        if any(k in low for k in keys) and sdg not in sdgs:
            sdgs.append(sdg)
    if not sdgs:
        sdgs = ["SDG 12: Responsible Consumption and Production"]
    return ", ".join(tags) if tags else "Not publicly available", "; ".join(sdgs)

def parse_sources(text):
    sec = get_section(text, "Sources", [])
    urls = re.findall(r"https?://\S+", sec)
    return sec, len(urls)

def parse_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    title_m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    org_name = title_m.group(1).strip() if title_m else os.path.basename(path)[:-3]
    facts = parse_quickfacts(text)
    overview = get_section(text, "Organisation Overview", [])
    business = get_section(text, "Business Model", [])
    activities = get_section(text, "Circular Economy Activities", [])
    partnerships = get_section(text, "Partnerships", [])
    impact = get_section(text, "Measurable Impact", [])
    assessment = get_section(text, "REUSE Foundation Assessment", [])
    verif_notes = get_section(text, "Verification Notes", [])
    sources_text, src_count = parse_sources(text)
    conf_name, conf_year, conf_impact, last_verified = parse_confidence_footer(text)
    overall_levels = [conf_name, conf_year, conf_impact]
    overall_score = round(sum(score(l) for l in overall_levels) / 3)
    overall_conf = "High" if overall_score >= 85 else "Medium" if overall_score >= 55 else "Low"
    priority = parse_priority(assessment)
    tags, sdgs = derive_tags_sdgs(activities, facts.get("Primary Category",""))
    slug = os.path.basename(path)[:-3]

    row = {
        "Organisation": org_name,
        "Country": facts.get("Country / HQ","Not publicly available"),
        "Status": facts.get("Status","Not publicly available"),
        "Official name (+source)": facts.get("Official Name","Not publicly available"),
        "Also known as": "Not publicly available",
        "Website": facts.get("Website","Not publicly available"),
        "Instagram": "Not publicly available",
        "Est. company size": "Not publicly available",
        "Primary customers": word_slice(get_section(text,"Customers",[]) or "Not publicly available", 60),
        "Year founded": facts.get("Year Founded","Not publicly available"),
        "Ownership status": facts.get("Ownership","Not publicly available"),
        "Core model": word_slice(business, 80) or "Not publicly available",
        "Geographic scope": facts.get("Country / HQ","Not publicly available"),
        "Categories": facts.get("Primary Category","Not publicly available"),
        "Key partners / customers": word_slice(partnerships, 60) or "Not publicly available",
        "Impact metrics": word_slice(impact, 80) or "Not publicly available",
        "Conf: name": conf_name,
        "Conf: year": conf_year,
        "Conf: impact": conf_impact,
        "Verification notes": word_slice(verif_notes, 80) or "See organisations/" + slug + ".md",
        "GitHub slug": slug,
        "Short summary": word_slice(overview, 75) or "Not publicly available",
        "Logo URL": "Not publicly available",
        "Featured image URL": "Not publicly available",
        "SEO description": word_slice(overview, 30) or "Not publicly available",
        "Primary colour": "Not publicly available",
        "Tags": tags,
        "Last verified date": last_verified,
        "Last updated date": last_verified,
        "Researcher": "AI",
        "Source count": src_count,
        "Overall confidence": overall_conf,
        "Overall confidence score": overall_score,
        "REUSE priority rating": priority,
        "SDGs": sdgs,
    }
    return row

if __name__ == "__main__":
    md_files = sys.argv[1:]
    out_rows = [parse_file(f) for f in md_files]
    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDNAMES)
    writer.writeheader()
    for r in out_rows:
        writer.writerow(r)
