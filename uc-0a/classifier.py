"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    # Implement rule-based classifier following uc-0a/agents.md and skills.md
    complaint_id = str(row.get("complaint_id", ""))
    description = (row.get("description") or "").strip()

    # default output
    out = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Normal",
        "reason": "",
        "flag": "",
    }

    if not description:
        out.update({"reason": "description missing", "flag": "MISSING_FIELDS"})
        return out

    desc_lower = description.lower()

    # category keyword lists (precedence order). Expanded to reduce 'Other' flags.
    categories = [
        # Pothole and road-surface related
        ("Pothole", [
            "pothole", "sinkhole", "big hole", "manhole", "manhole cover", "missing cover",
            "manhole cover missing", "road surface cracked", "surface cracked", "sinking", "subsidence",
            "footpath tiles", "tiles broken", "footpath", "upturned tiles", "tiles upturned"
        ]),
        # Flooding and drainage
        ("Flooding", [
            "flood", "waterlogging", "water logged", "flooded", "drain", "drain blocked",
            "stormwater", "drain blocked", "bridge approach floods", "bridge approach", "inaccessible"
        ]),
        # Garbage and waste
        ("Garbage", ["garbage", "trash", "waste", "dump", "dumping", "bulk waste", "bins", "dead animal", "dead animals", "animal carcass"]),
        # Streetlight / lighting
        ("Streetlight", ["streetlight", "lamp", "light not working", "no light", "lights out", "street lights out", "flickering", "sparking"]),
        # Water leaks and pipe failures
        ("WaterLeak", ["leak", "leaking pipe", "water leak", "pipe burst", "no water supply"]),
        # Tree related issues
        ("TreeIssue", ["fallen tree", "tree fallen", "overhanging branch", "tree branch", "tree branches"]),
        # Encroachment / unauthorized structures
        ("Encroachment", ["encroach", "encroachment", "unauthorized structure", "shop extension"]),
        # Noise and disturbances (expanded)
        ("Noise", ["noise", "loud music", "honking", "construction noise", "drilling", "wedding band", "band playing", "club music", "delivery trucks", "idling", "amplifiers", "music past midnight"]),
    ]

    matched_phrases = []
    matched_category = "Other"
    for cat, keywords in categories:
        for kw in keywords:
            if kw in desc_lower:
                matched_category = cat
                matched_phrases.append(kw)
                break
        if matched_category != "Other":
            break

    out["category"] = matched_category

    # priority rules
    injury_keywords = ["injury", "injured", "child", "kid", "school", "hospital", "fire", "electrocution", "gas leak", "drowning", "death", "serious injury", "fell", "fell last week", "risk of serious injury"]
    impact_keywords = ["blocked road", "major traffic", "large-scale flooding", "collapse", "fallen tree", "no water supply", "bridge becomes inaccessible", "inaccessible", "bridge approach floods", "passengers standing in water", "commuters stranded"]

    priority = "Normal"
    if any(kw in desc_lower for kw in injury_keywords):
        priority = "Urgent"
    elif any(kw in desc_lower for kw in impact_keywords):
        priority = "High"
    out["priority"] = priority

    # build reason: prefer exact phrase from description that matched category or priority
    reason = ""
    # try to find matched category phrase in original description (preserve original casing)
    for phrase in matched_phrases:
        idx = desc_lower.find(phrase)
        if idx != -1:
            # extract the original substring
            reason = description[idx: idx + len(phrase)]
            break

    # if no category phrase found, try to find a priority trigger
    if not reason:
        for kw in injury_keywords + impact_keywords:
            idx = desc_lower.find(kw)
            if idx != -1:
                reason = description[idx: idx + len(kw)]
                break

    if not reason:
        # fallback: take first 60 chars of description
        reason = (description[:60]).rstrip()

    # apply truncation limit
    if len(reason) > 120:
        reason = reason[:120]

    # if category is Other due to no match, set NEEDS_REVIEW and include text
    if out["category"] == "Other":
        out["flag"] = "NEEDS_REVIEW"
        # include phrase to indicate uncertainty
        if "uncertain mapping" not in reason.lower():
            reason = (reason + " — uncertain mapping")[:120]

    out["reason"] = reason
    return out


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    # Read input CSV, classify rows, write results CSV. Robust to bad rows.
    with open(input_path, newline='', encoding='utf-8') as infp:
        reader = csv.DictReader(infp)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, 'w', newline='', encoding='utf-8') as outf:
            writer = csv.DictWriter(outf, fieldnames=fieldnames)
            writer.writeheader()
            for idx, row in enumerate(reader, start=1):
                try:
                    # ensure keys are present as expected
                    normalized = {k: v for k, v in row.items()}
                    # keep complaint_id if present, else create a placeholder
                    if not normalized.get('complaint_id'):
                        normalized['complaint_id'] = f"MISSING_ID_{idx}"
                    result = classify_complaint(normalized)
                except Exception as e:
                    # on error, write a fallback row and continue
                    cid = row.get('complaint_id') or f"ERROR_ROW_{idx}"
                    result = {
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Normal",
                        "reason": f"error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW",
                    }
                writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
