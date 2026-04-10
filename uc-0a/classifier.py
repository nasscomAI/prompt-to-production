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
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_RULES = {
    "Pothole": ["pothole", "pit", "crater"],
    "Flooding": ["flood", "waterlogging", "water logging", "overflow"],
    "Streetlight": ["streetlight", "street light", "light not working", "dark street", "lamp post"],
    "Waste": ["garbage", "waste", "trash", "dump", "litter"],
    "Noise": ["noise", "loud", "speaker", "honking", "construction sound"],
    "Road Damage": ["road damage", "broken road", "crack", "damaged road", "road caved"],
    "Heritage Damage": ["heritage", "monument", "historic wall", "statue damage"],
    "Heat Hazard": ["heat", "heatwave", "no shade", "extreme temperature"],
    "Drain Blockage": ["drain", "sewer", "blockage", "clogged", "choked drain"],
}

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

def detect_priority(desc: str) -> str:
    d = normalize(desc)
    for kw in SEVERITY_KEYWORDS:
        if kw in d:
            return "Urgent"
    return "Standard"

def detect_category(desc: str):
    d = normalize(desc)
    matches = []

    for cat, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in d:
                matches.append(cat)
                break

    if len(matches) == 1:
        return matches[0], ""
    elif len(matches) > 1:
        # ambiguous - choose first but flag
        return matches[0], "NEEDS_REVIEW"
    else:
        return "Other", "NEEDS_REVIEW"

def build_reason(desc: str, category: str, priority: str, flag: str) -> str:
    d = normalize(desc)
    matched = []

    # Mention severity keyword if urgent
    if priority == "Urgent":
        for kw in SEVERITY_KEYWORDS:
            if kw in d:
                matched.append(kw)
                break

    # Mention category keyword
    for kw in CATEGORY_RULES.get(category, []):
        if kw in d:
            matched.append(kw)
            break

    if not matched:
        matched_text = "no clear keyword"
    else:
        matched_text = ", ".join(matched)

    if flag == "NEEDS_REVIEW":
        return f"Detected keywords: {matched_text}; complaint is ambiguous and needs review."
    return f"Detected keywords: {matched_text}; mapped to {category} with {priority} priority."

def classify_complaint(description: str):
    category, flag = detect_category(description)
    priority = detect_priority(description)
    reason = build_reason(description, category, priority, flag)
    return category, priority, reason, flag

def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    # Ensure output columns exist
    out_fields = fieldnames.copy()
    for col in ["category", "priority", "reason", "flag"]:
        if col not in out_fields:
            out_fields.append(col)

    for row in rows:
        desc = row.get("description", "")
        category, priority, reason, flag = classify_complaint(desc)
        # enforce allowed category values
        if category not in ALLOWED_CATEGORIES:
            category = "Other"
            if not flag:
                flag = "NEEDS_REVIEW"

        row["category"] = category
        row["priority"] = priority
        row["reason"] = reason
        row["flag"] = flag

    with open(output_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Wrote: {args.output}")

if __name__ == "__main__":
    main()