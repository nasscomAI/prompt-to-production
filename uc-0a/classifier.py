import argparse
import csv
import json

TAXONOMY = {
    "sanitation": ["missed_pickup", "overflowing_bin", "dead_animal"],
    "water": ["no_water", "leakage", "contamination"],
    "roads": ["pothole", "blocked_drain", "fallen_tree"],
    "streetlights": ["light_out", "flickering", "pole_damage"],
    "parks": ["grass_overgrown", "playground_damage", "illegal_dumping"]
}

KEYWORDS = {
    "sanitation": {
        "missed_pickup": ["garbage not collected", "trash not collected", "missed pickup", "waste not collected"],
        "overflowing_bin": ["overflowing bin", "bin full", "garbage overflowing", "trash overflowing"],
        "dead_animal": ["dead animal", "dead dog", "dead cat", "animal carcass"]
    },
    "water": {
        "no_water": ["no water", "water not coming", "no supply", "water outage"],
        "leakage": ["water leak", "pipe leak", "leakage", "burst pipe"],
        "contamination": ["dirty water", "contaminated water", "smelly water", "brown water"]
    },
    "roads": {
        "pothole": ["pothole", "road damaged", "big hole", "road crack"],
        "blocked_drain": ["blocked drain", "drain clogged", "waterlogging", "drain overflow"],
        "fallen_tree": ["fallen tree", "tree blocking road", "tree collapsed"]
    },
    "streetlights": {
        "light_out": ["streetlight not working", "light out", "street light off", "lamp not working"],
        "flickering": ["flickering light", "blinking light", "light flashing"],
        "pole_damage": ["pole damaged", "electric pole bent", "streetlight pole broken"]
    },
    "parks": {
        "grass_overgrown": ["grass overgrown", "uncut grass", "park grass too high"],
        "playground_damage": ["swing broken", "slide broken", "playground damaged", "play area unsafe"],
        "illegal_dumping": ["garbage dumped in park", "illegal dumping", "waste in park"]
    }
}

HIGH_SEVERITY = [
    "fire", "sparking", "electrical hazard", "injury", "accident",
    "danger", "unsafe", "blocked access", "completely blocked", "contaminated water"
]

MEDIUM_SEVERITY = [
    "not working", "broken", "overflowing", "leak", "damaged", "delayed"
]


def detect_severity(text):
    t = text.lower()
    if any(word in t for word in HIGH_SEVERITY):
        return "high"
    if any(word in t for word in MEDIUM_SEVERITY):
        return "medium"
    return "low"


def classify_complaint(text):
    t = text.lower()
    matches = []

    for department, subcats in KEYWORDS.items():
        for sub_category, keywords in subcats.items():
            for keyword in keywords:
                if keyword in t:
                    matches.append((department, sub_category, keyword))

    severity = detect_severity(text)

    if not matches:
        return {
            "department": "sanitation",
            "sub_category": "missed_pickup",
            "severity": severity,
            "rationale": "No exact taxonomy match found. Assigned closest safe default and flagged ambiguity.",
            "ambiguity_flag": True
        }

    department, sub_category, keyword = matches[0]
    ambiguity = len(set((m[0], m[1]) for m in matches)) > 1

    rationale = f"Matched complaint text to taxonomy using keyword '{keyword}'."
    if ambiguity:
        rationale += " Multiple possible matches found, so ambiguity is flagged."

    return {
        "department": department,
        "sub_category": sub_category,
        "severity": severity,
        "rationale": rationale,
        "ambiguity_flag": ambiguity
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    results = []

    with open(args.input, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            complaint = row["complaint_text"]
            result = classify_complaint(complaint)
            result["complaint_id"] = row["complaint_id"]
            results.append(result)

    with open(args.output, "w", encoding="utf-8") as outfile:
        for item in results:
            outfile.write(json.dumps(item) + "\n")

    print(f"Classification results written to {args.output}")


if __name__ == "__main__":
    main()
