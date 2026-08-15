"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

HERITAGE_KEYWORDS = ["heritage", "historic", "historical", "ancient", "cobblestone", "monument", "step well", "old city"]
LIGHTING_KEYWORDS = ["streetlight", "street light", "lights out", "light out", "unlit", "flicker", "spark", "lamp", "substation", "darkness"]
POTHOLE_KEYWORDS = ["pothole"]
FLOODING_KEYWORDS = ["flood", "waterlog", "submerg", "rainwater"]
DRAIN_KEYWORDS = ["drain", "sewer"]
WASTE_KEYWORDS = ["garbage", "waste", "rubbish", "trash", "litter", "bin", "dumped", "dumping", "overflow", "dead animal", "debris"]
NOISE_KEYWORDS = ["music", "noise", "loud", "amplifier", "drill", "honk", "idling", "band"]
HEAT_KEYWORDS = ["heat", "hot", "temperatur", "°c", "celsius", "melt", "burn", "heatwave", "full sun"]
ROAD_KEYWORDS = ["road", "footpath", "pavement", "paving", "manhole", "bridge", "tarmac", "crater", "crack", "sink", "subsid", "buckle", "collaps", "curb", "kerb", "highway"]


def _priority(description: str) -> str:
    low = description.lower()
    if any(k in low for k in URGENT_KEYWORDS):
        return "Urgent"
    return "Standard"


def _category(description: str):
    low = description.lower()
    if any(k in low for k in HERITAGE_KEYWORDS) and any(k in low for k in LIGHTING_KEYWORDS):
        return "Other", True
    if any(k in low for k in POTHOLE_KEYWORDS):
        return "Pothole", False
    if any(k in low for k in FLOODING_KEYWORDS):
        if ("blocked" in low or "blockage" in low) and "risk" in low:
            return "Drain Blockage", False
        return "Flooding", False
    if any(k in low for k in DRAIN_KEYWORDS):
        return "Drain Blockage", False
    if any(k in low for k in LIGHTING_KEYWORDS):
        return "Streetlight", False
    if any(k in low for k in WASTE_KEYWORDS):
        return "Waste", False
    if any(k in low for k in NOISE_KEYWORDS):
        return "Noise", False
    if any(k in low for k in HERITAGE_KEYWORDS):
        return "Heritage Damage", False
    if any(k in low for k in HEAT_KEYWORDS):
        return "Heat Hazard", False
    if any(k in low for k in ROAD_KEYWORDS):
        return "Road Damage", False
    return "Other", True


def _reason(description: str) -> str:
    first = description.strip().split(".")[0].strip()
    return f'The description says "{first}".'


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    category, ambiguous = _category(description)
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": _priority(description),
        "reason": _reason(description),
        "flag": "NEEDS_REVIEW" if ambiguous else "",
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": "",
                "flag": "NEEDS_REVIEW",
            })
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
