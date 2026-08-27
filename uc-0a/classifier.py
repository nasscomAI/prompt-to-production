import argparse
import csv
import re

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']


def has(text, word):
    return word in text


def has_word(text, word):
    return bool(re.search(r'(?<![a-z])' + re.escape(word) + r'(?![a-z])', text))


def classify_complaint(row: dict) -> dict:
    desc = row.get('description', '').lower()
    cid = row.get('complaint_id', '')

    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    is_urgent = any(kw in desc for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"

    is_flooding = has(desc, "flood")
    is_drain = has_word(desc, "drain") or has(desc, "manhole")
    is_streetlight = has(desc, "streetlight") or has(desc, "lamp post") or (has(desc, "lights") and has(desc, "out")) or has(desc, "unlit")
    is_heritage = has(desc, "heritage") or has(desc, "ancient") or has(desc, "historic") or has(desc, "museum") or has(desc, "tagore")
    is_road = has_word(desc, "road") or has(desc, "footpath") or has(desc, "paving") or has(desc, "bridge") or has(desc, "tarmac") or has(desc, "cobblestones") or has(desc, "buckled") or has(desc, "subsidence") or has(desc, "subsided")
    is_heat = has_word(desc, "sun") or has(desc, "melting") or has(desc, "temperature") or has(desc, "heatwave") or has(desc, "burns") or has(desc, "bubbling") or has(desc, "unbearable") or has_word(desc, "heat")

    ambiguous_pairs = []

    if is_flooding and is_drain:
        ambiguous_pairs.append(("Flooding", "Drain Blockage"))
    if is_heritage and is_road:
        ambiguous_pairs.append(("Heritage Damage", "Road Damage"))
    if is_streetlight and is_heritage:
        ambiguous_pairs.append(("Streetlight", "Heritage Damage"))
    if is_heritage and has(desc, "waste"):
        ambiguous_pairs.append(("Heritage Damage", "Waste"))
    if is_heritage and (has(desc, "noise") or has(desc, "amplifiers") or has(desc, "music")):
        ambiguous_pairs.append(("Heritage Damage", "Noise"))

    if ambiguous_pairs:
        pair_str = " and ".join([f"{a}/{b}" for a, b in ambiguous_pairs])
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous between {pair_str}."
    else:
        if has(desc, "pothole"):
            category = "Pothole"
        elif is_flooding:
            category = "Flooding"
        elif is_heat:
            category = "Heat Hazard"
        elif is_drain:
            category = "Drain Blockage"
        elif is_streetlight:
            category = "Streetlight"
        elif has(desc, "garbage") or has(desc, "waste") or (has(desc, "dead") and has(desc, "animal")):
            category = "Waste"
        elif has(desc, "music") or has(desc, "drilling") or has(desc, "delivery") or has(desc, "amplifiers") or has(desc, "noise"):
            category = "Noise"
        elif is_heritage:
            category = "Heritage Damage"
        elif is_road:
            category = "Road Damage"
        else:
            category = "Other"

        if not flag and category == "Other" and has(desc, "heritage") and has(desc, "streetlight"):
            flag = "NEEDS_REVIEW"

        if not reason:
            matched_words = []
            for w in SEVERITY_KEYWORDS + ["pothole", "flood", "drain", "streetlight", "garbage", "waste", "music", "noise", "road", "heritage", "melting", "temperature"]:
                if w in desc:
                    matched_words.append(f"'{w}'")
                    if len(matched_words) >= 3:
                        break
            if matched_words:
                reason = f"Classified as {category} based on keywords: {', '.join(matched_words)}."
            else:
                reason = f"Classified as {category} based on description."

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error during classification: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
