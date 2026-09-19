"""UC-0A - Complaint Classifier"""
import argparse
import csv
import re

CATEGORY_RULES = [  # order = tie-break priority
    ("Heritage Damage", ["heritage", "monument", "temple", "fort", "statue", "historic"]),
    ("Heat Hazard", ["heatwave", "heat", "scorching", "sunstroke"]),
    ("Drain Blockage", ["drain", "sewer", "clogged", "blocked"]),
    ("Flooding", ["flood", "waterlog", "submerged", "inundat"]),
    ("Pothole", ["pothole"]),
    ("Streetlight", ["streetlight", "street light", "lamp", "light not working", "lights out"]),
    ("Waste", ["garbage", "waste", "trash", "dump", "litter", "overflowing bin"]),
    ("Noise", ["noise", "loud", "music", "speaker", "honking"]),
    ("Road Damage", ["road damage", "crack", "sinking", "broken road", "road surface", "cave-in", "footpath"]),
]
SEVERITY = ["injur\\w*", "child\\w*", "school\\w*", "hospital\\w*", "ambulance\\w*",
            "fire", "hazard\\w*", "fell", "collapse\\w*"]
LOW_WORDS = ["minor", "cosmetic", "faded", "paint"]


def classify_complaint(row: dict) -> dict:
    cid = (row.get("complaint_id") or "").strip()
    desc = (row.get("description") or "").strip()
    if not desc:
        return {"complaint_id": cid, "category": "Other", "priority": "Standard",
                "reason": "Description is empty; cannot classify.", "flag": "NEEDS_REVIEW"}

    text = desc.lower()
    matches = []
    for cat, words in CATEGORY_RULES:
        for w in words:
            if re.search(r"\b" + re.escape(w), text):
                matches.append((cat, w))
                break

    if not matches:
        category, flag = "Other", "NEEDS_REVIEW"
        cat_reason = "no category keyword found in description"
    else:
        category = matches[0][0]
        flag = "NEEDS_REVIEW" if len(matches) > 1 else ""
        cat_reason = "; ".join(f'"{w}" -> {c}' for c, w in matches)

    sev = None
    for pat in SEVERITY:
        m = re.search(r"\b" + pat + r"\b", text)
        if m:
            sev = m.group(0)
            break
    if sev:
        priority = "Urgent"
        reason = f'Severity word "{sev}" in description; category from {cat_reason}.'
    elif any(w in text for w in LOW_WORDS):
        priority = "Low"
        reason = f"Minor/cosmetic wording in description; category from {cat_reason}."
    else:
        priority = "Standard"
        reason = f"No severity keyword; category from {cat_reason}."

    return {"complaint_id": cid, "category": category, "priority": priority,
            "reason": reason, "flag": flag}


def batch_classify(input_path: str, output_path: str):
    fields = ["complaint_id", "category", "priority", "reason", "flag"]
    out = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            try:
                out.append(classify_complaint(row))
            except Exception as e:
                out.append({"complaint_id": (row.get("complaint_id") or f"row{i}"),
                            "category": "Other", "priority": "Standard",
                            "reason": f"Row failed to classify: {e}", "flag": "NEEDS_REVIEW"})
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")