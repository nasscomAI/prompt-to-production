import argparse
import csv
import os
from typing import List, Tuple

def classify_complaint(row: dict) -> dict:
    allowed_categories = [
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
    urgent_terms = [
        "injury",
        "child",
        "school",
        "hospital",
        "ambulance",
        "fire",
        "hazard",
        "fell",
        "collapse",
    ]
    low_terms = ["minor", "small", "cosmetic"]
    def norm_text(v: str) -> str:
        return (v or "").strip()
    complaint_id = norm_text(row.get("complaint_id") or row.get("id") or "")
    title = norm_text(row.get("title"))
    description = norm_text(row.get("description"))
    text = " ".join([t for t in [title, description] if t]).lower()
    if not text:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing or empty; classification not possible.",
            "flag": "NEEDS_REVIEW",
        }
    def any_in(words: List[str]) -> Tuple[bool, List[str]]:
        hits = [w for w in words if w in text]
        return (len(hits) > 0, hits)
    cat = None
    cited_terms: List[str] = []
    pothole_hit, pothole_terms = any_in(["pothole"])
    drain_hit, drain_terms = any_in(["drain blocked", "blocked drain", "drain", "sewer", "clog", "choke", "choked"])
    light_hit, light_terms = any_in(["streetlight", "street light", "streetlights", "lights out", "light out", "lamp", "dark at night", "flickering", "sparking"])
    flood_hit, flood_terms = any_in(["flood", "flooded", "waterlogged", "knee-deep", "knee deep", "waterlogging"])
    waste_hit, waste_terms = any_in(["garbage", "trash", "waste", "dumped", "bins", "dead animal"])
    noise_hit, noise_terms = any_in(["noise", "loudspeaker", "music", "honking", "past midnight"])
    heat_hit, heat_terms = any_in(["heat hazard", "heatwave", "heat wave", "heat"])
    heritage_hit, heritage_terms = any_in(["heritage", "historic", "monument", "fort", "temple", "museum"])
    road_hit, road_terms = any_in(["road surface", "crack", "cracked", "sinking", "uneven", "broken tiles", "footpath tiles", "manhole cover missing", "manhole missing", "manhole cover"])
    if pothole_hit:
        cat = "Pothole"
        cited_terms += pothole_terms
    elif light_hit:
        cat = "Streetlight"
        cited_terms += light_terms
    elif drain_hit:
        cat = "Drain Blockage"
        cited_terms += drain_terms
    elif flood_hit:
        cat = "Flooding"
        cited_terms += flood_terms
    elif waste_hit:
        cat = "Waste"
        cited_terms += waste_terms
    elif noise_hit:
        cat = "Noise"
        cited_terms += noise_terms
    elif heat_hit:
        cat = "Heat Hazard"
        cited_terms += heat_terms
    elif heritage_hit and any(t in text for t in ["damage", "broken", "defaced", "vandal", "crack", "collapse"]):
        cat = "Heritage Damage"
        cited_terms += heritage_terms
    elif road_hit:
        cat = "Road Damage"
        cited_terms += road_terms
    else:
        cat = "Other"
    urgent_hit, urgent_terms_hits = any_in(urgent_terms)
    low_hit, low_terms_hits = any_in(low_terms)
    if urgent_hit:
        priority = "Urgent"
        cited_terms += urgent_terms_hits
    elif low_hit:
        priority = "Low"
        cited_terms += low_terms_hits
    else:
        priority = "Standard"
    ambiguous_flag = ""
    signals = sum([
        1 if pothole_hit else 0,
        1 if light_hit else 0,
        1 if drain_hit else 0,
        1 if flood_hit else 0,
        1 if waste_hit else 0,
        1 if noise_hit else 0,
        1 if heat_hit else 0,
        1 if heritage_hit else 0,
        1 if road_hit else 0,
    ])
    if cat == "Other" and signals > 1:
        ambiguous_flag = "NEEDS_REVIEW"
    reason_terms = []
    seen = set()
    for term in cited_terms:
        if term not in seen:
            seen.add(term)
            reason_terms.append(term)
    reason_snippet = ", ".join(reason_terms[:3]) if reason_terms else (description[:60] + "..." if len(description) > 60 else description)
    reason = f'Based on "{reason_snippet}" in the description.'
    result = {
        "complaint_id": complaint_id,
        "category": cat if cat in allowed_categories else "Other",
        "priority": priority,
        "reason": reason,
        "flag": ambiguous_flag,
    }
    return result


def batch_classify(input_path: str, output_path: str):
    rows_out: List[dict] = []
    try:
        with open(input_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception:
                    cid = (row.get("complaint_id") or row.get("id") or "").strip() if isinstance(row, dict) else ""
                    result = {
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Row processing failed; insufficient or malformed input.",
                        "flag": "NEEDS_REVIEW",
                    }
                rows_out.append(result)
    except Exception:
        rows_out = [{
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": "Input file could not be read.",
            "flag": "NEEDS_REVIEW",
        }]
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows_out:
            writer.writerow({
                "complaint_id": r.get("complaint_id", ""),
                "category": r.get("category", "Other"),
                "priority": r.get("priority", "Standard"),
                "reason": r.get("reason", ""),
                "flag": r.get("flag", ""),
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
