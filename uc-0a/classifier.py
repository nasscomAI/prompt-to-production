#!/usr/bin/env python
"""UC-0A Complaint Classifier with RICE enforcement."""

import csv
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

# ===== CONFIGURATION =====
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

SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category detection patterns (order matters for specificity)
CATEGORY_PATTERNS = [
    ("Drain Blockage", [r"drain", r"blocked", r"blockage", r"manhole"]),
    ("Heritage Damage", [r"heritage", r"old city", r"historic"]),
    ("Pothole", [r"pothole", r"hole.*wide", r"sinking", r"tyre damage"]),
    ("Flooding", [r"flood", r"water", r"knee-deep", r"waterlogged", r"submerged", r"stranded"]),
    ("Streetlight", [r"streetlight", r"street light", r"lights? out", r"flickering", r"sparking"]),
    ("Waste", [r"garbage", r"waste", r"trash", r"litter", r"bins?", r"dump"]),
    ("Noise", [r"noise", r"music", r"sound", r"loud", r"midnight"]),
    ("Road Damage", [r"road.*crack", r"road.*damage", r"surface.*crack", r"cracked.*sinking"]),
]


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    """Classify a single complaint row.
    
    Returns:
        Dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # Step 1: Check for severity keywords
    found_severity = False
    severity_words = []
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            # Check if it's in a negative context
            if f"no {keyword}" not in description and f"not {keyword}" not in description:
                found_severity = True
                severity_words.append(keyword)
    
    priority = "Urgent" if found_severity else "Standard"
    
    # Step 2: Classify by category
    matches = []
    for category, patterns in CATEGORY_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, description):
                matches.append(category)
                break
    
    if not matches:
        category = "Other"
        reason = "No clear classification indicators found."
        flag = ""
    elif len(matches) == 1:
        category = matches[0]
        reason = f"{category.lower()} identified: keywords match complaint description."
        flag = ""
    else:
        # Ambiguous - multiple matches
        category = matches[0]  # Pick first match
        reason = f"Multiple possible categories detected ({', '.join(matches)}). Primary: {category}."
        flag = "NEEDS_REVIEW"
    
    # Step 3: Build reason with specific citations
    if category == "Pothole" and "pothole" in description:
        reason = "Pothole damage: complaint mentions 'pothole' and 'tyre damage'."
    elif category == "Flooding" and any(w in description for w in ["flood", "water", "submerged"]):
        flood_words = [w for w in ["flooded", "water", "stranded"] if w in description]
        reason = f"Flooding: complaint describes '{', '.join(flood_words)}' conditions."
    elif category == "Streetlight" and any(w in description for w in ["light", "dark", "out"]):
        reason = "Streetlight issue: complaint mentions lighting deficiency."
    elif category == "Waste" and any(w in description for w in ["garbage", "waste", "bins"]):
        reason = "Waste management: complaint describes garbage/waste accumulation."
    elif category == "Noise":
        reason = "Noise complaint: music/sound mentioned."
    elif category == "Road Damage":
        reason = "Road damage: surface deterioration or cracks noted."
    elif category == "Drain Blockage":
        reason = "Drain blockage: drainage system mentioned as problematic."
    elif category == "Heritage Damage":
        reason = "Heritage site: complaint references historic area."
    
    # Add severity note if urgent
    if priority == "Urgent":
        reason += f" URGENT: '{severity_words[0]}' detected."
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Read complaints from CSV, classify, and write results."""
    results = []
    urgent_count = 0
    flagged_count = 0
    
    # Read input
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} complaints...")
    
    # Classify each row
    for row in rows:
        result = classify_complaint(row)
        result["complaint_id"] = row["complaint_id"]
        results.append(result)
        
        if result["priority"] == "Urgent":
            urgent_count += 1
        if result["flag"] == "NEEDS_REVIEW":
            flagged_count += 1
    
    # Write output
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✓ Classification complete: {len(results)} rows processed")
    print(f"  - Urgent: {urgent_count}")
    print(f"  - Standard: {len(results) - urgent_count}")
    print(f"  - Flagged for review: {flagged_count}")
    print(f"✓ Output written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify citizen complaints")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
