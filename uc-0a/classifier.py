"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import sys

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "hole in road", "hole in the road"],
    "Flooding": ["flood", "waterlog", "submerged", "standing water"],
    "Streetlight": ["streetlight", "street light", "lamp post", "light not working", "unlit", "lights out", "darkness"],
    "Waste": ["garbage", "waste", "trash", "litter", "dumping", "rubbish", "solid waste", "dead animal", "carcass", "decaying"],
    "Noise": ["noise", "loud", "honking", "disturbance", "noisy", "construction noise", "music", "DJ", "speaker", "drilling", "amplifier", "playing music"],
    "Road Damage": ["road damage", "damaged road", "cracked road", "broken road", "deteriorated road", "road surface", "footpath", "pavement", "subsidence", "subsided", "buckled"],
    "Heritage Damage": ["heritage", "monument", "historical", "historic", "ancient structure", "heritage site", "cobblestone", "step well"],
    "Heat Hazard": ["heat", "sunstroke", "heatwave", "extreme temperature", "heat hazard", "temperature", "melting"],
    "Drain Blockage": ["drain", "blockage", "sewer", "clogged", "drainage", "clog"],
}

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
LOW_SEVERITY_KEYWORDS = ["minor", "slight", "small", "inconvenience", "cosmetic"]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()
    matched = []
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in desc_lower:
                matched.append(cat)
                break
    matched = list(dict.fromkeys(matched))

    if len(matched) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched) == 1:
        category = matched[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    urgent_found = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    if urgent_found:
        priority = "Urgent"
    else:
        low_found = [kw for kw in LOW_SEVERITY_KEYWORDS if kw in desc_lower]
        priority = "Low" if low_found else "Standard"

    cited = []
    if category != "Other":
        for kw in CATEGORY_KEYWORDS[category]:
            if kw in desc_lower:
                idx = desc_lower.index(kw)
                cited.append(description[idx:idx + len(kw)])
                if len(cited) >= 2:
                    break
    else:
        for cat, kws in CATEGORY_KEYWORDS.items():
            for kw in kws:
                if kw in desc_lower:
                    idx = desc_lower.index(kw)
                    cited.append(description[idx:idx + len(kw)])
                    if len(cited) >= 2:
                        break
            if len(cited) >= 2:
                break

    reason_parts = []
    if cited:
        quoted = ", ".join(f"'{w}'" for w in cited)
        reason_parts.append(f"Description mentions {quoted}")
        if category != "Other":
            reason_parts.append(f"indicating {category}")
    else:
        reason_parts.append("Description does not clearly match any category")

    if urgent_found:
        reason_parts.append(f"with urgent keyword(s): {', '.join(urgent_found)}")

    reason = "; ".join(reason_parts) + "."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            print("Warning: Empty CSV", file=sys.stderr)
            return
        col_map = {}
        for col in reader.fieldnames:
            cl = col.lower().replace(" ", "_")
            if cl in ("complaint_id", "id", "complaintid"):
                col_map[col] = "complaint_id"
            elif cl in ("description", "desc", "complaint", "text", "details"):
                col_map[col] = "description"

        for i, raw in enumerate(reader, start=2):
            try:
                row = {}
                for orig, mapped in col_map.items():
                    row[mapped] = raw.get(orig, "")
                rows.append(row)
            except Exception as e:
                print(f"Warning: Skipping row {i}: {e}", file=sys.stderr)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as e:
            print(f"Warning: Failed to classify complaint {row.get('complaint_id', '?')}: {e}", file=sys.stderr)
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": "Classification error",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
