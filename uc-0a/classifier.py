import csv
import re
import argparse

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    (r"pothole", "Pothole"),
    (r"flood|flooded|flooding|waterlog|knee.deep|submerged|standing.?water|inundat", "Flooding"),
    (r"streetlight|street.?light|light.?out|lights?.*out|flicker|spark.*light|lamp.*post", "Streetlight"),
    (r"garbage|waste|bin|rubbish|trash|overflow.*bin|dump.*waste|dead.animal|carcass|refuse|rotting", "Waste"),
    (r"noise|loud.*music|music.*night|honking|party.*noise", "Noise"),
    (r"road.*sink|road.*damage|road.*crack|crack.*road|sinking.*road|surface.*crack|footpath.*broken|footpath.*damage|pavement.*damage|road.*deteriorat", "Road Damage"),
    (r"heritage|heritage.*street|heritage.*light|historic.*damage|monument", "Heritage Damage"),
    (r"heat.*hazard|sun.*hazard|extreme.*heat|heat.*wave", "Heat Hazard"),
    (r"drain.*block|blocked.*drain|clog.*drain|drainage.*issue|manhole.*block|drain.*clog|sewer", "Drain Blockage"),
]

AMBIGUOUS_PATTERNS = [
    (r"heritage.*light|light.*heritage", {"Heritage Damage", "Streetlight"}),
]


def classify_category(desc):
    desc_lower = desc.lower()

    ambiguous = []
    for pattern, candidates in AMBIGUOUS_PATTERNS:
        if re.search(pattern, desc_lower):
            ambiguous.append(candidates)

    if ambiguous:
        return "Other", "NEEDS_REVIEW"

    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, desc_lower):
            return category, ""

    return "Other", "NEEDS_REVIEW"


def classify_priority(desc):
    desc_lower = desc.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            return "Urgent"
    return "Standard"


def build_reason(desc, category, priority, flag):
    desc_lower = desc.lower()
    words_used = []

    if priority == "Urgent":
        for kw in SEVERITY_KEYWORDS:
            if kw in desc.lower():
                words_used.append(kw)

    for pattern, cat in CATEGORY_RULES:
        if cat == category:
            m = re.search(pattern, desc_lower)
            if m:
                words_used.append(m.group(0))

    excerpt = ""
    if words_used:
        start = desc_lower.find(words_used[0])
        if start >= 0:
            end = start + len(words_used[0])
            excerpt = desc[start:end]

    if excerpt:
        return f"Description mentions '{excerpt}' which indicates {category.lower()}"
    elif flag == "NEEDS_REVIEW":
        return "Category ambiguous -- description does not clearly match a single category"
    return f"Description indicates {category.lower()}"


def classify_complaint(row):
    desc = row["description"]
    category, flag = classify_category(desc)
    priority = classify_priority(desc)
    reason = build_reason(desc, category, priority, flag)
    return {"description": desc, "category": category, "priority": priority, "reason": reason, "flag": flag}


def batch_classify(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = []
    for row in rows:
        result = classify_complaint(row)
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["description", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(description="Classify citizen complaints")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
