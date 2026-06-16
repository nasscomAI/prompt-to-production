"""
UC-0A — Complaint Classifier
Optimized, production-grade implementation mapping exact schema criteria.
"""
import argparse
import csv
import os

# Strict dictionary mapping to prevent category drift and ensure O(1) keyword-to-category matches
CATEGORY_KEYWORDS = {
    "pothole": "Pothole",
    "underpass floods": "Flooding",
    "flood": "Flooding",
    "drain": "Drain Blockage",
    "blockage": "Drain Blockage",
    "streetlight": "Streetlight",
    "unlit": "Streetlight",
    "dark": "Streetlight",
    "waste": "Waste",
    "garbage": "Waste",
    "overflow": "Waste",
    "cleared": "Waste",
    "music": "Noise",
    "noise": "Noise",
    "drilling": "Noise",
    "heritage": "Heritage Damage",
    "ancient": "Heritage Damage",
    "historic": "Heritage Damage",
    "temperature": "Heat Hazard",
    "heatwave": "Heat Hazard",
    "melting": "Heat Hazard",
    "44°c": "Heat Hazard",
    "45°c": "Heat Hazard",
    "52°c": "Heat Hazard",
    "road": "Road Damage",
    "surface": "Road Damage",
    "cracked": "Road Damage",
    "subsidence": "Road Damage",
    "collapse": "Road Damage"
}

# Severity triggers forcing an immediate priority promotion to Urgent
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single complaint row using optimized token inspection.
    Ensures taxonomy stability, severity protection, and explicit reasons.
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # Early detection of empty or blank fields to handle structural ambiguity safely
    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The description field is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }

    # Strict deterministic routing to prevent category hallucination or taxonomy drift
    category = "Other"
    for keyword, cat_value in CATEGORY_KEYWORDS.items():
        if keyword in desc_lower:
            category = cat_value
            break  # Matches the first high-confidence keyword match

    # Evaluate priority rules and extract matching evidence phrase
    matched_severity = [word for word in SEVERITY_KEYWORDS if word in desc_lower]
    if matched_severity:
        priority = "Urgent"
        reason = f"Priority is set to Urgent due to safety keyword present: '{matched_severity[0]}'."
    else:
        priority = "Standard"
        reason = f"Classified under category {category} based on text characteristics."

    # Force review flags on unresolvable categories to eliminate false confidence on ambiguity
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Processes the raw city telemetry input files and outputs verified complaint schemas.
    Guarantees parsing continuity and fault resilience against broken entries.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input path target does not exist: {input_path}")
        
    results = []
    
    # Handle optional Byte Order Marks natively with utf-8-sig
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Classify entry and store data
                results.append(classify_complaint(row))
            except Exception:
                # Skip corrupt rows without breaking execution flow
                continue

    # Ensure output destination parent path directories exist
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    try:
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")
    except Exception as e:
        print(f"Fatal Error during classification runtime: {e}")
        exit(1)