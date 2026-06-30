import argparse
import csv
import re
import sys


URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_RULES = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "knee.dee", "stranded", "under water", "submerged", "water logging"]),
    ("Streetlight", ["streetlight", "lights out", "flickering", "sparking", "dark at night", "no light"]),
    ("Waste", ["garbage", "overflowing bin", "waste", "dead animal", "dumped"]),
    ("Noise", ["noise", "music", "loud", "playing past"]),
    ("Road Damage", ["cracked", "sinking", "footpath", "manhole cover", "broken tile", "upturned", "road surface"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heat", "heatwave", "hot"]),
    ("Drain Blockage", ["drain blocked", "drain clogged"]),
]

AMBIGUOUS_PAIRS = [
    ({"Flooding", "Drain Blockage"}, {"flooded", "drain"}),
    ({"Heritage Damage", "Streetlight"}, {"heritage", "light"}),
]


def classify_complaint(description):
    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Empty description",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    matched_categories = []
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if re.search(re.escape(kw), desc_lower):
                matched_categories.append(category)
                break

    if not matched_categories:
        return {
            "category": "Other",
            "priority": _determine_priority(desc_lower),
            "reason": f"Description does not clearly match any category: \"{description[:80]}\"",
            "flag": "NEEDS_REVIEW",
        }

    unique_cats = list(dict.fromkeys(matched_categories))

    needs_review = False
    for pair, triggers in AMBIGUOUS_PAIRS:
        if pair.issubset(set(unique_cats)):
            words_in_desc = sum(1 for t in triggers if re.search(re.escape(t), desc_lower))
            if words_in_desc >= len(triggers) - 1:
                needs_review = True
                break

    if len(unique_cats) > 2:
        needs_review = True

    picked = unique_cats[0]

    severity_desc_words = [w for w in URGENT_KEYWORDS if re.search(r"\b" + re.escape(w) + r"\b", desc_lower)]
    priority = "Urgent" if severity_desc_words else "Standard"

    cited_words = _build_reason(picked, description, desc_lower, severity_desc_words)

    return {
        "category": picked,
        "priority": priority,
        "reason": cited_words,
        "flag": "NEEDS_REVIEW" if needs_review else "",
    }


def _determine_priority(desc_lower):
    for kw in URGENT_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", desc_lower):
            return "Urgent"
    return "Standard"


def _build_reason(category, description, desc_lower, severity_words):
    reason_parts = []
    reason_parts.append(f"Description mentions \"{_extract_snippet(description, category)}\"")
    if severity_words:
        reason_parts.append(f"severity keyword(s): {', '.join(severity_words)}")
    return ". ".join(reason_parts) + "."


def _extract_snippet(description, category):
    for cat, keywords in CATEGORY_RULES:
        if cat == category:
            for kw in keywords:
                match = re.search(re.escape(kw), description.lower())
                if match:
                    start = max(0, match.start() - 10)
                    end = min(len(description), match.end() + 20)
                    return description[start:end].strip()
    return description[:60].strip()


def batch_classify(input_path, output_path):
    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "description" not in reader.fieldnames:
            print(f"Error: input CSV must contain a 'description' column. Found columns: {reader.fieldnames}", file=sys.stderr)
            sys.exit(1)
        for row in reader:
            rows.append(row)

    if not rows:
        print("Error: input CSV is empty", file=sys.stderr)
        sys.exit(1)

    for i, row in enumerate(rows):
        try:
            result = classify_complaint(row.get("description", ""))
            row["category"] = result["category"]
            row["priority"] = result["priority"]
            row["reason"] = result["reason"]
            row["flag"] = result["flag"]
        except Exception as e:
            print(f"Warning: row {i} (id={row.get('complaint_id', '?')}) failed: {e}", file=sys.stderr)
            row["category"] = "Other"
            row["priority"] = "Low"
            row["reason"] = f"Classification error: {e}"
            row["flag"] = "NEEDS_REVIEW"

    fieldnames = list(rows[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Classified {len(rows)} complaints -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV with complaint descriptions")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
