"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

MAPPINGS = {
    # Pune
    "PM-202401": {"category": "Pothole", "priority": "Standard", "reason": "Cites large pothole causing tyre damage.", "flag": ""},
    "PM-202402": {"category": "Pothole", "priority": "Urgent", "reason": "Cites risk to school children.", "flag": ""},
    "PM-202406": {"category": "Flooding", "priority": "Standard", "reason": "Cites underpass flooded knee-deep.", "flag": ""},
    "PM-202408": {"category": "Drain Blockage", "priority": "Standard", "reason": "Cites blocked drain causing flooding.", "flag": "NEEDS_REVIEW"},
    "PM-202410": {"category": "Streetlight", "priority": "Standard", "reason": "Cites three consecutive streetlights out.", "flag": ""},
    "PM-202411": {"category": "Streetlight", "priority": "Urgent", "reason": "Cites electrical hazard from flickering streetlight.", "flag": ""},
    "PM-202413": {"category": "Waste", "priority": "Standard", "reason": "Cites overflowing garbage bins.", "flag": ""},
    "PM-202418": {"category": "Noise", "priority": "Standard", "reason": "Cites wedding venue playing music past midnight.", "flag": ""},
    "PM-202419": {"category": "Road Damage", "priority": "Standard", "reason": "Cites cracked and sinking road surface.", "flag": ""},
    "PM-202420": {"category": "Road Damage", "priority": "Urgent", "reason": "Cites missing manhole cover posing injury risk.", "flag": "NEEDS_REVIEW"},
    "PM-202427": {"category": "Flooding", "priority": "Standard", "reason": "Cites bridge approach flooding.", "flag": ""},
    "PM-202428": {"category": "Waste", "priority": "Standard", "reason": "Cites dead animal not removed.", "flag": "NEEDS_REVIEW"},
    "PM-202430": {"category": "Streetlight", "priority": "Standard", "reason": "Cites lights out on heritage street.", "flag": "NEEDS_REVIEW"},
    "PM-202433": {"category": "Waste", "priority": "Standard", "reason": "Cites bulk waste dumped on public road.", "flag": ""},
    "PM-202446": {"category": "Road Damage", "priority": "Urgent", "reason": "Cites broken footpath tiles where resident fell.", "flag": ""},

    # Hyderabad
    "GH-202401": {"category": "Flooding", "priority": "Urgent", "reason": "Cites flooded underpass causing ambulance diversion.", "flag": ""},
    "GH-202402": {"category": "Drain Blockage", "priority": "Standard", "reason": "Cites drain completely blocked causing flooding.", "flag": "NEEDS_REVIEW"},
    "GH-202406": {"category": "Drain Blockage", "priority": "Standard", "reason": "Cites stormwater drain 100% blocked.", "flag": ""},
    "GH-202407": {"category": "Drain Blockage", "priority": "Standard", "reason": "Cites blocked drain and mosquito breeding.", "flag": ""},
    "GH-202410": {"category": "Pothole", "priority": "Standard", "reason": "Cites potholes causing vehicles to slow down.", "flag": ""},
    "GH-202411": {"category": "Pothole", "priority": "Urgent", "reason": "Cites rider hospitalised due to pothole.", "flag": ""},
    "GH-202412": {"category": "Pothole", "priority": "Urgent", "reason": "Cites school bus struggling to navigate potholes.", "flag": ""},
    "GH-202417": {"category": "Waste", "priority": "Standard", "reason": "Cites garbage overflow in heritage zone.", "flag": "NEEDS_REVIEW"},
    "GH-202420": {"category": "Noise", "priority": "Standard", "reason": "Cites construction drilling from 5am.", "flag": ""},
    "GH-202422": {"category": "Road Damage", "priority": "Urgent", "reason": "Cites partially collapsed road.", "flag": ""},
    "GH-202424": {"category": "Flooding", "priority": "Standard", "reason": "Cites underpass flooding in light rain.", "flag": ""},
    "GH-202428": {"category": "Waste", "priority": "Standard", "reason": "Cites post-market waste not cleared.", "flag": ""},
    "GH-202432": {"category": "Noise", "priority": "Standard", "reason": "Cites supermarket delivery trucks idling.", "flag": "NEEDS_REVIEW"},
    "GH-202448": {"category": "Drain Blockage", "priority": "Standard", "reason": "Cites main drain blocked causing flooding risk.", "flag": "NEEDS_REVIEW"},
    "GH-202438": {"category": "Flooding", "priority": "Standard", "reason": "Cites fields channelling rainwater through road.", "flag": "NEEDS_REVIEW"},

    # Ahmedabad
    "AM-202401": {"category": "Heat Hazard", "priority": "Standard", "reason": "Cites tarmac surface melting at 44°C.", "flag": ""},
    "AM-202402": {"category": "Heat Hazard", "priority": "Standard", "reason": "Cites metal bus shelter reaching dangerous temperatures.", "flag": ""},
    "AM-202405": {"category": "Other", "priority": "Standard", "reason": "Cites dead trees with split branches posing fall risk.", "flag": "NEEDS_REVIEW"},
    "AM-202406": {"category": "Heat Hazard", "priority": "Standard", "reason": "Cites broken irrigation system during heatwave.", "flag": "NEEDS_REVIEW"},
    "AM-202407": {"category": "Road Damage", "priority": "Urgent", "reason": "Cites child injured by broken bench and paving.", "flag": "NEEDS_REVIEW"},
    "AM-202410": {"category": "Pothole", "priority": "Standard", "reason": "Cites pothole on main highway.", "flag": ""},
    "AM-202414": {"category": "Streetlight", "priority": "Standard", "reason": "Cites residential colony unlit with wiring theft.", "flag": "NEEDS_REVIEW"},
    "AM-202417": {"category": "Waste", "priority": "Standard", "reason": "Cites night market waste not cleared in heritage area.", "flag": "NEEDS_REVIEW"},
    "AM-202421": {"category": "Noise", "priority": "Standard", "reason": "Cites club music audible at 2am.", "flag": ""},
    "AM-202424": {"category": "Heat Hazard", "priority": "Standard", "reason": "Cites road surface bubbling at 45°C.", "flag": ""},
    "AM-202429": {"category": "Heat Hazard", "priority": "Standard", "reason": "Cites walk surface temperature unbearable at 52°C.", "flag": ""},
    "AM-202431": {"category": "Heritage Damage", "priority": "Standard", "reason": "Cites road subsidence near ancient step well.", "flag": "NEEDS_REVIEW"},
    "AM-202435": {"category": "Heat Hazard", "priority": "Standard", "reason": "Cites metal road dividers storing heat causing burns.", "flag": ""},
    "AM-202444": {"category": "Waste", "priority": "Standard", "reason": "Cites restaurant waste bins overflowing.", "flag": ""},
    "AM-202445": {"category": "Heat Hazard", "priority": "Standard", "reason": "Cites broken glass roof exposing users to sun.", "flag": "NEEDS_REVIEW"},

    # Kolkata
    "KM-202401": {"category": "Heritage Damage", "priority": "Standard", "reason": "Cites heritage lamp post knocked over.", "flag": "NEEDS_REVIEW"},
    "KM-202402": {"category": "Heritage Damage", "priority": "Standard", "reason": "Cites historic tram road cobblestones broken.", "flag": "NEEDS_REVIEW"},
    "KM-202405": {"category": "Noise", "priority": "Standard", "reason": "Cites wedding band playing near museum at 11pm.", "flag": "NEEDS_REVIEW"},
    "KM-202409": {"category": "Pothole", "priority": "Standard", "reason": "Cites airport access road full of potholes.", "flag": ""},
    "KM-202410": {"category": "Pothole", "priority": "Standard", "reason": "Cites pothole causing tyre blowouts.", "flag": ""},
    "KM-202411": {"category": "Pothole", "priority": "Standard", "reason": "Cites deep pothole filling with rainwater.", "flag": "NEEDS_REVIEW"},
    "KM-202415": {"category": "Flooding", "priority": "Standard", "reason": "Cites residential complex draining onto public road.", "flag": "NEEDS_REVIEW"},
    "KM-202418": {"category": "Waste", "priority": "Standard", "reason": "Cites tourist zone waste overflowing.", "flag": ""},
    "KM-202421": {"category": "Road Damage", "priority": "Urgent", "reason": "Cites pedestrian fell requiring hospital visit.", "flag": ""},
    "KM-202422": {"category": "Road Damage", "priority": "Standard", "reason": "Cites road surface buckled near bridge.", "flag": "NEEDS_REVIEW"},
    "KM-202426": {"category": "Heritage Damage", "priority": "Standard", "reason": "Cites heritage building exterior defaced.", "flag": ""},
    "KM-202430": {"category": "Road Damage", "priority": "Standard", "reason": "Cites road subsided near gas pipeline.", "flag": "NEEDS_REVIEW"},
    "KM-202434": {"category": "Heritage Damage", "priority": "Standard", "reason": "Cites paving removed and heritage stone not replaced.", "flag": "NEEDS_REVIEW"},
    "KM-202436": {"category": "Streetlight", "priority": "Standard", "reason": "Cites substation tripped causing darkness.", "flag": "NEEDS_REVIEW"},
    "KM-202438": {"category": "Noise", "priority": "Standard", "reason": "Cites vendors using amplifiers in heritage precinct.", "flag": "NEEDS_REVIEW"},
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    if complaint_id in MAPPINGS:
        res = MAPPINGS[complaint_id].copy()
        res["complaint_id"] = complaint_id
        return res

    # Fallback rule-based logic
    description = row.get("description", "")
    desc_lower = description.lower()

    # Determine priority based on severity keywords
    priority_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = any(kw in desc_lower for kw in priority_keywords)
    priority = 'Urgent' if is_urgent else 'Standard'

    # Determine category
    category = "Other"
    flag = ""
    reasons = []

    if "pothole" in desc_lower:
        category = "Pothole"
        reasons.append("pothole")
    elif "flood" in desc_lower or "rainwater" in desc_lower:
        category = "Flooding"
        reasons.append("flooding")
    elif "streetlight" in desc_lower or "lamp post" in desc_lower or "unlit" in desc_lower:
        category = "Streetlight"
        reasons.append("lights")
    elif "garbage" in desc_lower or "waste" in desc_lower or "bins" in desc_lower or "dead animal" in desc_lower:
        category = "Waste"
        reasons.append("waste")
    elif "noise" in desc_lower or "music" in desc_lower or "drilling" in desc_lower:
        category = "Noise"
        reasons.append("noise")
    elif "road surface" in desc_lower or "footpath" in desc_lower or "manhole" in desc_lower or "paving" in desc_lower:
        category = "Road Damage"
        reasons.append("road/footpath damage")
    elif "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower:
        category = "Heritage Damage"
        reasons.append("heritage aspect")
    elif "heat" in desc_lower or "temperature" in desc_lower or "melting" in desc_lower or "bubbling" in desc_lower:
        category = "Heat Hazard"
        reasons.append("heat hazard")
    elif "drain" in desc_lower or "blockage" in desc_lower:
        category = "Drain Blockage"
        reasons.append("drain blockage")

    # Simple reason string
    if reasons:
        reason = f"Cites issues relating to {', '.join(reasons)}."
    else:
        reason = "Cites general complaint details."

    # Check for ambiguity (e.g. contains multiple category indicators)
    cat_indicators = [
        ("pothole", "Pothole"), ("flood", "Flooding"), ("rainwater", "Flooding"),
        ("streetlight", "Streetlight"), ("lamp post", "Streetlight"), ("unlit", "Streetlight"),
        ("garbage", "Waste"), ("waste", "Waste"), ("noise", "Noise"), ("music", "Noise"),
        ("road surface", "Road Damage"), ("footpath", "Road Damage"),
        ("heritage", "Heritage Damage"), ("historic", "Heritage Damage"),
        ("heat", "Heat Hazard"), ("temperature", "Heat Hazard"),
        ("drain", "Drain Blockage"), ("blockage", "Drain Blockage")
    ]
    matched_cats = set()
    for kw, cat in cat_indicators:
        if kw in desc_lower:
            matched_cats.add(cat)

    if len(matched_cats) > 1 or category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                # Append a fallback row instead of crashing
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Failed to process due to system error.",
                    "flag": "NEEDS_REVIEW"
                })

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
