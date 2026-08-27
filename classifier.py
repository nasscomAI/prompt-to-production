"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def _has_word(desc_lower: str, word: str) -> bool:
    return bool(re.search(rf'\b{re.escape(word)}\b', desc_lower))


def _category_scores(desc_lower: str) -> dict:
    scores = {}

    scores["Pothole"] = 1 if "pothole" in desc_lower else 0

    flooding_score = 0
    if "flood" in desc_lower or "flooded" in desc_lower or "flooding" in desc_lower:
        flooding_score += 1
    if "submerged" in desc_lower:
        flooding_score += 1
    if "waterlogged" in desc_lower:
        flooding_score += 1
    if _has_word(desc_lower, "rain"):
        flooding_score += 1
    scores["Flooding"] = flooding_score

    scores["Drain Blockage"] = 1 if re.search(
        r"drain.*\bblock|blocked drain|drainage|sewer", desc_lower
    ) else 0

    streetlight_score = sum(1 for w in [
        "streetlight", "street light", "lights out", "lamp post",
        "flickering", "unlit"
    ] if w in desc_lower)
    if "darkness" in desc_lower or "no lights" in desc_lower:
        streetlight_score += 1
    if "wiring theft" in desc_lower or "substation" in desc_lower:
        streetlight_score += 1
    scores["Streetlight"] = streetlight_score

    waste_score = sum(1 for w in [
        "garbage", "waste", "dead animal", "dump", "trash"
    ] if w in desc_lower)
    if "overflow" in desc_lower and "bin" in desc_lower:
        waste_score += 1
    if "not cleared" in desc_lower:
        waste_score += 1
    if "health concern" in desc_lower or "health risk" in desc_lower:
        waste_score += 0.5
    scores["Waste"] = waste_score

    noise_score = sum(1 for w in [
        "music", "noise", "loud", "party", "speaker",
        "amplifier", "drilling", "idling", "band", "festival"
    ] if w in desc_lower)
    if "wedding" in desc_lower and ("music" in desc_lower or "band" in desc_lower or "playing" in desc_lower):
        noise_score += 1
    if "construction" in desc_lower and "drilling" in desc_lower:
        noise_score += 1
    if "truck" in desc_lower or "delivery" in desc_lower:
        noise_score += 0.5
    scores["Noise"] = noise_score

    road_score = sum(1 for w in [
        "road surface", "cracked", "sinking", "manhole cover",
        "footpath", "tiles", "upturned", "pavement", "road damage",
        "collapsed", "subsided", "subsidence", "buckled",
        "gas pipeline", "gas leak"
    ] if w in desc_lower)
    if "road" in desc_lower and "collapse" in desc_lower:
        road_score += 1
    scores["Road Damage"] = road_score

    heritage_score = 0
    if "heritage" in desc_lower:
        if any(w in desc_lower for w in [
            "damage", "broken", "lights out", "safety", "knocked",
            "defaced", "stone", "concern", "zone", "precinct", "lamp"
        ]):
            heritage_score += 1
        if "not replaced" in desc_lower or "not restored" in desc_lower:
            heritage_score += 1
    if "historic" in desc_lower and "heritage" not in desc_lower:
        if any(w in desc_lower for w in ["cobblestone", "broken", "damage"]):
            heritage_score += 1
    if "ancient" in desc_lower and "heritage" in desc_lower:
        heritage_score += 1
    scores["Heritage Damage"] = heritage_score

    heat_score = 0
    if re.search(r"\b\d{2}\s*[°]?\s*[cC]\b", desc_lower):
        heat_score += 1
    if re.search(r"heatwave|heat wave|\bheat\b|hot\b|burning", desc_lower):
        heat_score += 1
    if "temperature" in desc_lower:
        heat_score += 1
    if "melting" in desc_lower:
        heat_score += 0.5
    scores["Heat Hazard"] = heat_score

    return scores


def _resolve_category(scores: dict, desc_lower: str) -> tuple:
    scored = [(cat, sc) for cat, sc in scores.items() if sc >= 1.0]
    if not scored:
        return "Other", "NEEDS_REVIEW"

    max_score = max(sc for _, sc in scored)
    top = [cat for cat, sc in scored if sc == max_score]

    if "Heritage Damage" in top and "Waste" in top and scores["Waste"] >= 1:
        top.remove("Heritage Damage")

    if "Heritage Damage" in top and "Noise" in top:
        top.remove("Heritage Damage")

    if len(top) == 1:
        return top[0], ""

    if "Flooding" in top and "Drain Blockage" in top:
        flood_words = sum(1 for w in ["flooded", "flooding", "water", "submerged"] if w in desc_lower)
        if flood_words > 0:
            return "Flooding", ""
        return "Drain Blockage", ""

    if "Heritage Damage" in top:
        return "Heritage Damage", ""

    if "Road Damage" in top and "Heat Hazard" in top:
        return "Road Damage", ""

    return "Other", "NEEDS_REVIEW"


def _matched_keywords(desc_lower: str, category: str) -> list:
    keyword_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flooding", "flooded", "flood", "submerged", "waterlogged", "rain"],
        "Drain Blockage": ["drain", "drainage", "sewer"],
        "Streetlight": ["streetlight", "street light", "lights out", "lamp post",
                         "flickering", "unlit", "darkness", "no lights",
                         "wiring theft", "substation"],
        "Waste": ["garbage", "waste", "dead animal", "dump", "trash",
                  "overflow", "bin", "not cleared", "health concern", "health risk"],
        "Noise": ["music", "noise", "loud", "party", "speaker", "amplifier",
                  "drilling", "idling", "band", "festival", "wedding",
                  "construction", "truck", "delivery"],
        "Road Damage": ["road surface", "cracked", "sinking", "manhole cover",
                        "footpath", "tiles", "upturned", "pavement", "road damage",
                        "collapsed", "subsided", "subsidence", "buckled",
                        "gas pipeline", "gas leak"],
        "Heritage Damage": ["heritage", "historic", "ancient", "cobblestone"],
        "Heat Hazard": ["heatwave", "heat wave", "heat", "hot", "burning",
                        "temperature", "melting"],
    }
    matched = []
    for phrase in keyword_map.get(category, []):
        if phrase in desc_lower:
            matched.append(phrase)
    return matched


def classify_complaint(row: dict) -> dict:
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()
    days_open = row.get("days_open", "0").strip()
    try:
        days_open_val = int(days_open)
    except (ValueError, TypeError):
        days_open_val = 0
    if not complaint_id:
        complaint_id = "UNKNOWN"
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    desc_lower = description.lower()
    has_severity = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    scores = _category_scores(desc_lower)
    category, flag = _resolve_category(scores, desc_lower)
    max_score = max(scores.values()) if scores else 0
    if has_severity:
        priority = "Urgent"
    elif max_score >= 1.0:
        priority = "Standard"
    else:
        priority = "Low"
    if days_open_val > 30 and priority == "Standard":
        priority = "Urgent"
    matched = _matched_keywords(desc_lower, category)
    kw_str = ", ".join(f"'{w}'" for w in matched[:5])
    if kw_str:
        reason = f"Contains keywords {kw_str} indicating {category.lower()}."
    else:
        reason = f"Contains phrase '{description[:80]}...' indicating {category.lower()}."
    if flag == "NEEDS_REVIEW" and category == "Other":
        reason = f"Description '{description[:80]}...' is ambiguous; no category strongly matches."
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    results = [classify_complaint(row) for row in rows]
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
