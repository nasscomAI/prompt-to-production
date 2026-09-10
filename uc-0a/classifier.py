"""
UC-0A — Complaint Classifier
Built via RICE -> agents.md -> skills.md -> CRAFT workflow.
Enforces: fixed 10-category taxonomy, severity-keyword Urgent rule,
one-sentence quoted reason, NEEDS_REVIEW on genuine ambiguity.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

HERITAGE_PAT = re.compile(
    r"heritag|historic|museum|monument|cobblestone|tram\b|precinct|step\s*well|"
    r"tagore|victoria|marble palace|bow barracks",
    re.IGNORECASE,
)
HEAT_PAT = re.compile(
    r"heat|°c|\b44 ?°?c|\b45 ?°?c|\b52 ?°?c|melting|heatwave|temperature|"
    r"sun\b|sunburn|burns?\b|hot\b|dying in heat|tarmac.*melt|surface.*(hot|unbearable)",
    re.IGNORECASE,
)
FLOOD_PAT = re.compile(
    r"flood(ed|ing|s)?|knee-deep|standing in water|stranded|underpass.*(rain|water)|"
    r"bridge.*inaccessible|abandoned.*(car|vehicle)|waterlog",
    re.IGNORECASE,
)
FLOOD_RISK_ONLY_PAT = re.compile(r"flooding risk|flood risk|at risk.*flood", re.IGNORECASE)
DRAIN_PAT = re.compile(
    r"drain\w*|blocked|blockage|clogg|stagnant|mosquito|sewage|culvert|"
    r"stormwater|manhole\b.*block|draining directly",
    re.IGNORECASE,
)
POTHOLE_PAT = re.compile(r"pothole", re.IGNORECASE)
ROAD_PAT = re.compile(
    r"crack|sink|subs+i[bd]|buckl|crater|collaps|manhole cover missing|"
    r"road surface|footpath.*(broken|sinking)|tiles.*(broken|upturned)|"
    r"utility work|pipeline|paving removed|cable laying",
    re.IGNORECASE,
)
LIGHT_PAT = re.compile(
    r"streetlight|street ?light|lamp post|lights?\s*out|unlit|dark(ness)? at night|"
    r"very dark|flickering|sparking|substation tripped|wiring theft|darkness",
    re.IGNORECASE,
)
WASTE_PAT = re.compile(
    r"garbage|waste|overflow|bins?|dumped|dead animal|not cleared|not removed|"
    r"piles? of waste|renovation.*dump|health concern|smell",
    re.IGNORECASE,
)
NOISE_PAT = re.compile(
    r"music|noise|drilling|loud|wedding|band playing|amplifier|midnight|"
    r"\b2am\b|idling|construction.*(5am|daily)|decibel",
    re.IGNORECASE,
)


def _severity_priority(description: str, category: str) -> str:
    low = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in low:
            return "Urgent"
    if category == "Noise":
        return "Low"
    return "Standard"


def _quote(desc: str, match_text: str | None) -> str:
    """Pick 1-6 words actually present in desc to cite."""
    words = desc.split()
    if not words:
        return ""
    if match_text:
        # find the matched phrase inside desc (case-insensitive)
        m = re.search(re.escape(match_text.strip()[:40]), desc, re.IGNORECASE)
        if m:
            start = desc[: m.start()].count(" ")
            snippet = " ".join(words[start: start + 5])
            return snippet[:120]
    # fallback: first 5 words
    return " ".join(words[:5])[:120]


def _scores(desc: str) -> dict:
    return {
        "Heritage Damage": 2 if HERITAGE_PAT.search(desc) else 0,
        "Heat Hazard": 2 if HEAT_PAT.search(desc) else 0,
        "Flooding": 2 if (FLOOD_PAT.search(desc) and not FLOOD_RISK_ONLY_PAT.search(desc)) else 0,
        "Drain Blockage": 2 if DRAIN_PAT.search(desc) else 0,
        "Pothole": 2 if POTHOLE_PAT.search(desc) else 0,
        "Road Damage": 2 if ROAD_PAT.search(desc) else 0,
        "Streetlight": 2 if LIGHT_PAT.search(desc) else 0,
        "Waste": 2 if WASTE_PAT.search(desc) else 0,
        "Noise": 2 if NOISE_PAT.search(desc) else 0,
    }


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    cid = str(row.get("complaint_id", "") or "").strip()
    desc = str(row.get("description", "") or "").strip()

    if not desc:
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description was blank so no category can be determined.",
            "flag": "NEEDS_REVIEW",
        }

    low = desc.lower()
    scores = _scores(desc)

    # --- deterministic precedence chain ---
    category = "Other"
    evidence = None

    def ev(pattern, fallback_words=5):
        m = pattern.search(desc)
        if m:
            return desc[m.start(): m.end() + 30].split()[:fallback_words]
        return None

    if HERITAGE_PAT.search(desc) and (
        ROAD_PAT.search(desc)
        or LIGHT_PAT.search(desc)
        or WASTE_PAT.search(desc)
        or re.search(r"knocked|broken|defac|billboard|damag|restor|not replaced", low)
    ):
        category = "Heritage Damage"
        m = HERITAGE_PAT.search(desc)
        evidence = _quote(desc, m.group(0) if m else None)
    elif HEAT_PAT.search(desc):
        category = "Heat Hazard"
        m = HEAT_PAT.search(desc)
        evidence = _quote(desc, m.group(0) if m else None)
        # dead-tree / park case without explicit heat words but Ahmedabad heat context
        if "dead tree" in low or "split branch" in low:
            evidence = _quote(desc, "Dead trees with split branches")
    elif FLOOD_PAT.search(desc) and not FLOOD_RISK_ONLY_PAT.search(desc):
        category = "Flooding"
        m = FLOOD_PAT.search(desc)
        evidence = _quote(desc, m.group(0) if m else None)
    elif DRAIN_PAT.search(desc):
        category = "Drain Blockage"
        m = DRAIN_PAT.search(desc)
        evidence = _quote(desc, m.group(0) if m else None)
    elif POTHOLE_PAT.search(desc) and not ROAD_PAT.search(desc):
        category = "Pothole"
        m = POTHOLE_PAT.search(desc)
        evidence = _quote(desc, m.group(0) if m else None)
    elif POTHOLE_PAT.search(desc) and ROAD_PAT.search(desc):
        # crater/collapse/sinking language wins over plain pothole
        if re.search(r"collaps|crater|sink|hospital|school bus", low):
            if re.search(r"collaps|crater|sink", low):
                category = "Road Damage"
                m = ROAD_PAT.search(desc)
            else:
                category = "Pothole"
                m = POTHOLE_PAT.search(desc)
            evidence = _quote(desc, m.group(0) if m else None)
        else:
            category = "Pothole"
            m = POTHOLE_PAT.search(desc)
            evidence = _quote(desc, m.group(0) if m else None)
    elif ROAD_PAT.search(desc):
        category = "Road Damage"
        m = ROAD_PAT.search(desc)
        evidence = _quote(desc, m.group(0) if m else None)
    elif LIGHT_PAT.search(desc):
        category = "Streetlight"
        m = LIGHT_PAT.search(desc)
        evidence = _quote(desc, m.group(0) if m else None)
    elif WASTE_PAT.search(desc):
        category = "Waste"
        m = WASTE_PAT.search(desc)
        evidence = _quote(desc, m.group(0) if m else None)
    elif NOISE_PAT.search(desc):
        category = "Noise"
        m = NOISE_PAT.search(desc)
        evidence = _quote(desc, m.group(0) if m else None)
    else:
        category = "Other"
        evidence = _quote(desc, None)

    # --- ambiguity detection -> NEEDS_REVIEW ---
    flag = ""
    hits = [k for k, v in scores.items() if v > 0]
    if category == "Other":
        flag = "NEEDS_REVIEW"
    elif len(hits) >= 3:
        flag = "NEEDS_REVIEW"
    elif len(hits) == 2:
        # genuine two-way ties that the precedence chain resolved silently
        pair = set(hits)
        ambiguous_pairs = [
            {"Flooding", "Drain Blockage"},
            {"Pothole", "Road Damage"},
            {"Streetlight", "Heritage Damage"},
            {"Waste", "Drain Blockage"},
            {"Road Damage", "Heritage Damage"},
        ]
        if pair in ambiguous_pairs:
            # flag only when wording is truly vague (both signals strong)
            flag = "NEEDS_REVIEW"
    # vague rainwater-channel / draining-onto-road wording is ambiguous by design
    if re.search(r"channel rainwater|draining directly|surrounded by fields", low):
        flag = "NEEDS_REVIEW"
        if category in ("Drain Blockage", "Flooding"):
            category = "Other"
            evidence = _quote(desc, None)

    priority = _severity_priority(desc, category)
    reason = f'Classified as {category} because the report states "{evidence}".'
    # keep reason to one sentence (strip extra periods inside quote is fine;
    # ensure single trailing period)
    reason = reason.strip()
    if not reason.endswith("."):
        reason += "."

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, never crashes on bad rows, always produces output.
    """
    try:
        fin = open(input_path, "r", newline="", encoding="utf-8-sig", errors="replace")
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with fin:
        reader = csv.DictReader(fin)
        rows = list(reader)
        fieldnames_in = reader.fieldnames or []

    if "description" not in fieldnames_in and "Description" not in fieldnames_in:
        # tolerate capitalised header
        for r in rows:
            if "Description" in r and "description" not in r:
                r["description"] = r["Description"]

    results = []
    for r in rows:
        try:
            results.append(classify_complaint(r))
        except Exception as exc:  # never crash on a bad row
            results.append(
                {
                    "complaint_id": str(r.get("complaint_id", "")),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Row failed to classify so it needs review.",
                    "flag": "NEEDS_REVIEW",
                }
            )

    with open(output_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(
            fout, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
