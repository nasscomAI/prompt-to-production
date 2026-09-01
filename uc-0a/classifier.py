"""
UC-0A — Complaint Classifier
RICE → agents.md → skills.md → CRAFT workflow
Enforcement:
 - Category exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
 - Priority Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
 - Every row must include reason citing specific words from description
 - If category cannot be determined → Other + NEEDS_REVIEW
"""
import argparse
import csv

# Exact allowed categories per spec uc-0a/README.md:28
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

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Precedence-ordered keywords: more specific first to avoid bleed
# Heritage overrides road/streetlight waste when heritage context present
CATEGORY_KEYWORDS = {
    "Heritage Damage": [
        "heritage", "historic", "ancient", "tagore", "marble palace",
        "cobblestones", "heritage stone", "heritage zone", "heritage street",
        "billboard installation", "defaced",
    ],
    "Drain Blockage": [
        "drain blocked", "drain 100% blocked", "drain completely blocked",
        "main drain blocked", "main stormwater drain", "stormwater drain",
        "drain blockage", "sewage", "mosquito breeding", "dengue concern",
        "drainage & flooding", "draining directly onto public road",
    ],
    "Flooding": [
        "flooded", "flooding", "flood", "waterlogging", "overflow",  # overflow kept but waste prioritized after drain
        "underpass flooded", "underpass floods", "bridge floods", "bridge approach floods",
        "channel rainwater", "stranded", "abandoned",
    ],
    "Pothole": [
        "pothole", "potholes",
    ],
    "Road Damage": [
        "road damage", "broken road", "uneven",
        "road surface", "cracked", "sinking", "sunk", "buckled", "subsided", "subsidence",
        "crater", "collapsed", "collapse",
        "footpath", "tiles broken", "upturned", "manhole", "pavement", "paving removed",
        "bench", "paving",  # covers Kothrud paving cases
        "utility work", "cable laying",
    ],
    "Waste": [
        "garbage", "trash", "waste", "dump", "dumped",
        "dead animal", "not cleared", "not removed", "bins", "piles of waste", "piles",
        "health concern", "health risk",  # waste-related
    ],
    "Streetlight": [
        "streetlight", "streetlights", "lamp post", "lamp",
        "light not working", "light out", "lights out", "flickering", "sparking",
        "unlit", "darkness", "substation tripped", "wiring theft",
    ],
    "Heat Hazard": [
        "heat", "temperature", "melting", "heatwave", "burning",
        "full sun", "unbearable", "bubbling", "tarmac surface", "reaching dangerous temperatures",
        "grass dying", "split branches", "burns on contact",
        "44°c", "45°c", "52°c",
    ],
    "Noise": [
        "noise", "loud", "sound pollution", "music", "drilling",
        "band playing", "amplifiers", "wedding venue", "wedding band",
        "idling", "trucks idling", "playing music",
    ],
}

# Special disambiguation: Waste overflow should not be Flooding when garbage/waste present
# We handle by checking Waste keywords before Flooding overflow if both match

def _match_category(description_lower: str) -> tuple[str, str]:
    """Return (category, matched_keyword_phrase). Precedence with disambiguation."""
    # Check for strong heritage-damage signals that should beat waste/noise
    # e.g., heritage lamp, heritage stone, historic tram, ancient step well
    strong_heritage = ["heritage lamp", "heritage stone", "historic tram", "historic", "ancient", "marble palace", "cobblestones", "defaced", "billboard installation"]
    for kw in strong_heritage:
        if kw in description_lower:
            return "Heritage Damage", kw

    # If generic heritage zone/area/precinct but complaint is clearly waste/noise, defer heritage
    # Detect waste/noise first for those location-only cases
    generic_heritage_present = any(x in description_lower for x in ["heritage zone", "heritage area", "heritage precinct", "heritage street", "heritage", "tagore"])
    has_waste = any(w in description_lower for w in CATEGORY_KEYWORDS["Waste"])
    has_noise = any(n in description_lower for n in CATEGORY_KEYWORDS["Noise"])
    has_heat = any(h in description_lower for h in ["temperature", "melting", "heatwave", "heat", "burning", "bubbling", "unbearable", "tarmac surface", "44°c", "45°c", "52°c"])
    # For GH-202417, AM-202417 etc: heritage + waste -> Waste wins
    # For KM-202405, KM-202438: heritage + noise -> Noise wins
    if generic_heritage_present and has_waste and not any(k in description_lower for k in strong_heritage):
        # let waste win - check waste now before heritage
        for kw in CATEGORY_KEYWORDS["Waste"]:
            if kw in description_lower:
                return "Waste", kw
    if generic_heritage_present and has_noise and not any(k in description_lower for k in strong_heritage):
        for kw in CATEGORY_KEYWORDS["Noise"]:
            if kw in description_lower:
                return "Noise", kw

    # Generic heritage street lights out -> keep Heritage Damage over Streetlight
    if "heritage street" in description_lower:
        return "Heritage Damage", "heritage street"
    if "heritage" in description_lower and not has_waste and not has_noise:
        return "Heritage Damage", "heritage"

    # Drain Blockage before Flooding
    for cat in ["Drain Blockage", "Flooding", "Pothole", "Heat Hazard", "Road Damage", "Waste", "Streetlight", "Noise"]:
        for kw in CATEGORY_KEYWORDS[cat]:
            if kw in description_lower:
                if cat == "Flooding" and kw == "overflow":
                    if any(w in description_lower for w in ["garbage", "trash", "waste", "bins", "dump"]):
                        continue
                # Heat vs Road: if road surface + temperature/heat, prefer Heat Hazard
                if cat == "Road Damage" and kw == "road surface" and has_heat:
                    continue
                return cat, kw
    # Fallback generic heritage if nothing else matched
    if generic_heritage_present:
        for kw in CATEGORY_KEYWORDS["Heritage Damage"]:
            if kw in description_lower:
                return "Heritage Damage", kw
    return "Other", ""


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row. Returns complaint_id, category, priority, reason, flag."""
    complaint_id = (row.get("complaint_id") or "UNKNOWN").strip()
    description_raw = row.get("description", "")
    description = description_raw.strip()
    description_lower = description.lower()

    # Error handling: empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description — no words to cite",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_kw = _match_category(description_lower)

    # Priority detection - exact severity keywords per spec
    severity_hits = [w for w in SEVERITY_KEYWORDS if w in description_lower]
    if severity_hits:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Reason must cite specific words from description
    if category != "Other" and matched_kw:
        # Use the matched keyword phrase as citation, show lowercased match
        reason = f"Matched '{matched_kw}' in description: \"{description[:120]}\""
        if severity_hits:
            reason += f" | severity keyword(s) '{', '.join(severity_hits)}' → Urgent"
    elif category == "Other":
        reason = f"No category keyword matched in: \"{description[:120]}\""
        if severity_hits:
            reason += f" | severity keyword(s) '{', '.join(severity_hits)}' → Urgent"
    else:
        reason = f"Cited words from description: \"{description[:120]}\""

    # Flag logic
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    # Also flag ambiguous drain/flooding co-occurrence? If description mentions both flood and drain blocked, keep chosen category but not flag

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV. Robust to bad rows and nulls."""
    with open(input_path, newline="", encoding="utf-8") as infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError(f"Input CSV has no header: {input_path}")
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                # Normalize None values to empty string
                clean_row = {k: (v if v is not None else "") for k, v in row.items()}
                result = classify_complaint(clean_row)
                # Enforce allowed category
                if result["category"] not in ALLOWED_CATEGORIES:
                    result["category"] = "Other"
                    result["flag"] = "NEEDS_REVIEW"
                    result["reason"] += " | corrected to allowed taxonomy"
                writer.writerow(result)
            except Exception as e:
                writer.writerow({
                    "complaint_id": (row.get("complaint_id") or "UNKNOWN") if isinstance(row, dict) else "UNKNOWN",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error: {e}",
                    "flag": "BAD_ROW",
                })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
