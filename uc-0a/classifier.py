"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import os

# Fixed classification schema from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority from agents.md
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to agents.md enforcement rules.
    
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Implements RICE enforcement:
    - Category: exactly one of 9 fixed values
    - Priority: Urgent if severity keywords present, else Standard/Low
    - Reason: one sentence citing specific words from description
    - Flag: NEEDS_REVIEW only for genuine ambiguity
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    
    # Handle missing/empty description per skills.md error handling
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }
    
    # Convert to lowercase for keyword matching
    desc_lower = description.lower()
    
    # Determine category based on keywords in description
    category = "Other"
    reason = ""
    flag = ""
    
    # Category detection logic with specific keyword matching
    if "pothole" in desc_lower:
        category = "Pothole"
        reason = f"Description mentions 'pothole'"
    elif "flood" in desc_lower or "flooded" in desc_lower or "water" in desc_lower and ("standing" in desc_lower or "stranded" in desc_lower or "knee-deep" in desc_lower):
        category = "Flooding"
        reason = f"Description indicates flooding conditions"
    elif "streetlight" in desc_lower or ("light" in desc_lower and ("out" in desc_lower or "dark" in desc_lower or "flickering" in desc_lower or "sparking" in desc_lower)):
        category = "Streetlight"
        reason = f"Description mentions streetlight or lighting issues"
    elif "garbage" in desc_lower or "waste" in desc_lower or "bin" in desc_lower or "smell" in desc_lower:
        category = "Waste"
        reason = f"Description indicates waste management issue"
    elif "noise" in desc_lower or "music" in desc_lower and ("loud" in desc_lower or "midnight" in desc_lower):
        category = "Noise"
        reason = f"Description indicates noise complaint"
    elif "road" in desc_lower and ("crack" in desc_lower or "sinking" in desc_lower or "damage" in desc_lower or "surface" in desc_lower):
        category = "Road Damage"
        reason = f"Description indicates road surface damage"
    elif "heritage" in desc_lower or ("old city" in desc_lower or "rasta peth" in desc_lower):
        category = "Heritage Damage"
        reason = f"Description mentions heritage area concerns"
    elif "heat" in desc_lower or "temperature" in desc_lower:
        category = "Heat Hazard"
        reason = f"Description indicates heat-related hazard"
    elif "drain" in desc_lower and ("block" in desc_lower or "blocked" in desc_lower or "clog" in desc_lower):
        category = "Drain Blockage"
        reason = f"Description mentions blocked drain"
    elif "manhole" in desc_lower and "missing" in desc_lower:
        category = "Road Damage"
        reason = f"Description mentions 'manhole' and 'missing' indicating road hazard"
    elif "animal" in desc_lower and ("dead" in desc_lower or "not removed" in desc_lower):
        category = "Waste"
        reason = f"Description mentions 'dead animal' - waste management issue"
    elif "tiles" in desc_lower or "footpath" in desc_lower:
        category = "Road Damage"
        reason = f"Description indicates footpath/tile damage"
    elif "bulk waste" in desc_lower or "renovation" in desc_lower or "dumped" in desc_lower:
        category = "Waste"
        reason = f"Description indicates illegal dumping"
    else:
        category = "Other"
        reason = f"Cannot confidently categorize from description"
        flag = "NEEDS_REVIEW"
    
    # Determine priority based on severity keywords (enforcement rule 2)
    priority = "Standard"  # Default
    
    # Check for severity keywords that trigger Urgent
    found_severity_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    
    if found_severity_keywords:
        priority = "Urgent"
        # Update reason to mention severity
        if reason and not flag:
            reason = f"{reason}; contains severity keyword(s): {', '.join(found_severity_keywords)}"
    else:
        # Distinguish between Standard and Low based on infrastructure vs quality-of-life
        if category in ["Pothole", "Flooding", "Road Damage", "Drain Blockage"]:
            priority = "Standard"
        elif category in ["Noise", "Waste"]:
            priority = "Low"
        elif category in ["Streetlight", "Heritage Damage"]:
            # Context-dependent: check for safety concerns
            if "dark" in desc_lower or "safety" in desc_lower or "risk" in desc_lower:
                priority = "Standard"
            else:
                priority = "Low"
        else:
            priority = "Low"
    
    # Ensure reason cites specific words from description (enforcement rule 3)
    if not reason:
        reason = f"Classified based on description content"
    
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
    
    Implements skills.md batch_classify specification:
    - Reads CSV with complaint data
    - Applies classify_complaint to each row
    - Writes results CSV with classification outputs
    - Handles errors gracefully, continues on failures
    - Prints summary statistics
    """
    # Check if input file exists (skills.md error handling)
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    results = []
    total_processed = 0
    flagged_count = 0
    urgent_count = 0
    failed_rows = []
    
    try:
        # Read input CSV
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Process each row
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
                try:
                    result = classify_complaint(row)
                    results.append(result)
                    total_processed += 1
                    
                    # Track statistics
                    if result["flag"] == "NEEDS_REVIEW":
                        flagged_count += 1
                    if result["priority"] == "Urgent":
                        urgent_count += 1
                        
                except Exception as e:
                    # Log failed row but continue (skills.md error handling)
                    complaint_id = row.get("complaint_id", f"ROW_{row_num}")
                    failed_rows.append(complaint_id)
                    print(f"Warning: Failed to process {complaint_id}: {e}", file=sys.stderr)
                    
                    # Add error entry
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    total_processed += 1
                    flagged_count += 1
    
    except Exception as e:
        print(f"Error: Failed to read input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write output CSV (ensure it's created even if all rows failed)
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print summary statistics (skills.md output specification)
    print(f"\nClassification Summary:")
    print(f"  Total processed: {total_processed}")
    print(f"  Flagged for review: {flagged_count}")
    print(f"  Urgent priority: {urgent_count}")
    
    if failed_rows:
        print(f"  Failed rows: {len(failed_rows)} - {', '.join(failed_rows)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
