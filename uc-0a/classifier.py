"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Dict, Tuple

# Allowed categories from README.md
ALLOWED_CATEGORIES = {
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
}

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: Dict) -> Dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforcement rules from agents.md:
    1. Category must be exactly one of ALLOWED_CATEGORIES
    2. Priority is Urgent if description contains severity keywords, else Standard
    3. Reason must cite specific words from description
    4. Flag is NEEDS_REVIEW if ambiguous, else empty
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Determine priority based on severity keywords
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            priority = "Urgent"
            break
    
    # Classify category based on keywords in description
    category, reason, flag = _classify_category(description)
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _classify_category(description: str) -> Tuple[str, str, str]:
    """
    Classify complaint into category with reason and flag.
    Returns: (category, reason, flag)
    """
    desc_lower = description.lower()
    
    # Pothole detection
    if any(word in desc_lower for word in ["pothole", "pothole"]):
        reason = _extract_reason(description, ["pothole", "tyre", "damage", "wide"])
        return "Pothole", reason, ""
    
    # Flooding detection
    if any(word in desc_lower for word in ["flood", "flooded", "flooded", "stranded", "water", "wet"]):
        reason = _extract_reason(description, ["flooded", "knee-deep", "rain", "water", "stranded"])
        return "Flooding", reason, ""
    
    # Streetlight detection
    if any(word in desc_lower for word in ["streetlight", "light", "lighting", "sparking", "flickering"]):
        reason = _extract_reason(description, ["streetlight", "out", "dark", "sparking", "flickering"])
        return "Streetlight", reason, ""
    
    # Waste detection
    if any(word in desc_lower for word in ["waste", "garbage", "trash", "bin", "dump", "dumped"]):
        reason = _extract_reason(description, ["garbage", "bins", "waste", "overflowing", "dumped"])
        return "Waste", reason, ""
    
    # Drain blockage detection
    if any(word in desc_lower for word in ["drain", "blocked", "blockage"]):
        reason = _extract_reason(description, ["drain", "blocked"])
        return "Drain Blockage", reason, ""
    
    # Noise detection
    if any(word in desc_lower for word in ["noise", "music", "sound", "playing", "midnight"]):
        reason = _extract_reason(description, ["music", "midnight", "past midnight"])
        return "Noise", reason, ""
    
    # Road damage detection (cracks, sinking, broken tiles)
    if any(word in desc_lower for word in ["crack", "sinking", "surface", "tiles", "upturned", "broken"]):
        reason = _extract_reason(description, ["cracked", "sinking", "tiles", "broken", "upturned"])
        return "Road Damage", reason, ""
    
    # Heritage damage detection
    if any(word in desc_lower for word in ["heritage", "historic", "old city", "peth"]):
        reason = _extract_reason(description, ["heritage", "street", "lights"])
        return "Heritage Damage", reason, ""
    
    # Heat hazard detection
    if any(word in desc_lower for word in ["heat", "hazard", "electrical", "risk", "sparking"]):
        if "electrical" in desc_lower or "sparking" in desc_lower:
            reason = _extract_reason(description, ["electrical", "hazard", "sparking"])
            return "Heat Hazard", reason, ""
    
    # Manhole/Missing cover (safety risk)
    if any(word in desc_lower for word in ["manhole", "missing", "cover", "injury", "cyclist"]):
        reason = _extract_reason(description, ["manhole", "missing", "injury"])
        return "Road Damage", reason, ""
    
    # Bridge/infrastructure flooding
    if "bridge" in desc_lower and "flood" in desc_lower:
        reason = _extract_reason(description, ["bridge", "floods", "inaccessible"])
        return "Flooding", reason, ""
    
    # Dead animal (ambiguous - could be waste or health hazard)
    if "dead animal" in desc_lower:
        reason = _extract_reason(description, ["dead animal", "health concern"])
        return "Waste", reason, "NEEDS_REVIEW"
    
    # Default to Other with NEEDS_REVIEW if no clear match
    reason = _extract_reason(description, [])
    return "Other", reason, "NEEDS_REVIEW"


def _extract_reason(description: str, key_phrases: list) -> str:
    """
    Extract a one-sentence reason that cites specific words from description.
    Returns a concise summary with exact words from the description.
    """
    # Find first sentence or use first 150 chars
    sentences = description.split(".")
    first_sentence = sentences[0].strip() if sentences else description.strip()
    
    if len(first_sentence) > 150:
        first_sentence = first_sentence[:150] + "..."
    
    return first_sentence + "." if first_sentence and not first_sentence.endswith(".") else first_sentence


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles errors gracefully and logs them.
    """
    results = []
    error_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            if reader.fieldnames is None or 'description' not in reader.fieldnames:
                raise ValueError("Input CSV must have a 'description' column")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    error_count += 1
                    print(f"Warning: Error classifying row {row_num}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ROW-{row_num}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Classification error.",
                        "flag": "NEEDS_REVIEW"
                    })
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error reading input file: {e}")
    
    # Write results
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        raise Exception(f"Error writing output file: {e}")
    
    if error_count > 0:
        print(f"Completed with {error_count} errors out of {len(results)} rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
