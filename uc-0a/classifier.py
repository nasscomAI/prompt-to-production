"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import sys
import re

# --- STRICT SCHEMA ENFORCEMENT CONSTANTS ---
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Explicit classification mappings to avoid Taxonomy Drift and Hallucinated sub-categories
CATEGORY_MAPPINGS = {
    r"\bpothole[s]?\b": "Pothole",
    r"\b(flood|flooding|waterlogging|rainwater)\b": "Flooding",
    r"\b(streetlight[s]?|lamp[s]?|light[s]?)\b": "Streetlight",
    r"\b(waste|garbage|trash|dump|litter|debris)\b": "Waste",
    r"\b(noise|loud|sound|music)\b": "Noise",
    r"\b(road[s]?|asphalt|pavement|crack[s]?)\b": "Road Damage",
    r"\b(heritage|monument[s]?|statue[s]?|historic)\b": "Heritage Damage",
    r"\b(heat|hot|sunstroke|wave)\b": "Heat Hazard",
    r"\b(drain|sewer|clog|blockage|gutter)\b": "Drain Blockage"
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Skill Error Handling: Refuses non-string or missing descriptions; 
    explicitly flags genuinely ambiguous complaints as NEEDS_REVIEW instead 
    of predicting with false confidence; forces strict fallback to the exact 
    allowed taxonomy if taxonomy drift or hallucinated sub-categories are detected.
    """
    # Safeguard against malformed inputs or missing columns
    if not row or 'description' not in row or row['description'] is None:
        raise ValueError("Missing 'description' data field in complaint row.")
        
    description = str(row['description']).strip()
    if not description:
        raise ValueError("Description content field cannot be empty.")

    desc_lower = description.lower()
    complaint_id = row.get('complaint_id', '')

    # 1. Determine Priority Level (Prevents Severity Blindness)
    # Check if any designated severity keywords exist inside the raw string description
    is_urgent = any(keyword in desc_lower for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if is_urgent else "Standard"

    # 2. Extract Category matches via rigid Regex Patterns
    matched_categories = []
    matched_words = []
    
    for pattern, category_label in CATEGORY_MAPPINGS.items():
        matches = re.findall(pattern, desc_lower)
        if matches:
            matched_categories.append(category_label)
            # Flatten potential regex capture groups to collect clean cited words
            for match in matches:
                # Extract first element if match is a tuple/group structure
                word = match[0] if isinstance(match, tuple) else match
                if word:
                    matched_words.append(word)

    # Deduplicate matches
    matched_categories = list(set(matched_categories))
    matched_words = list(set(matched_words))

    # 3. Assess Ambiguity & Apply Review Flags (Prevents False Confidence)
    flag = ""
    if len(matched_categories) != 1 or "not sure" in desc_lower or "ambiguous" in desc_lower:
        flag = "NEEDS_REVIEW"
        category = "Other"
    else:
        category = matched_categories[0]

    # Enforce strict fallback structure to safeguard allowed taxonomy matching boundaries
    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    # 4. Synthesize One-Sentence Reason Justification (Prevents Missing Justification)
    if matched_words:
        cited_snippets = ", ".join(f"'{w}'" for w in sorted(matched_words)[:3])
        reason = f"Classified as {category} because the citizen description explicitly contains specific keywords matching {cited_snippets}."
    else:
        short_snippet = description[:35] + "..." if len(description) > 35 else description
        reason = f"Assigned fallback category due to generalized structural context reading '{short_snippet}'."

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
    
    Skill Error Handling: Aborts operation if the input file path is missing, 
    unreadable, or structurally corrupted; halts processing or logs malformed 
    rows if critical severity keywords trigger an invalid classification bypass; 
    ensures zero row-by-row structural category variance in the final layout.
    """
    # Check filesystem input validity parameters
    if not os.path.exists(input_path):
        print(f"Error: Target input file path '{input_path}' cannot be found.")
        sys.exit(1)

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                print("Error: Input CSV schema layout is corrupted or missing required 'description' field.")
                sys.exit(1)
            rows = list(reader)
    except Exception as e:
        print(f"Error: Failed to safely parse input CSV. Detail: {e}")
        sys.exit(1)

    # Establish the unified headers for output generation
    output_headers = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    
    # Preserve other metadata columns from source data if they exist
    for field in reader.fieldnames:
        if field not in output_headers and field not in ['category', 'priority_flag', 'priority']:
            output_headers.append(field)

    # Prepare output container folders
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_headers)
            writer.writeheader()

            for index, row in enumerate(rows, start=1):
                try:
                    # Run target single-row processing skill pipeline
                    result = classify_complaint(row)
                    
                    # Merge classification outputs back safely with matching row metadata
                    output_row = row.copy()
                    output_row.update(result)
                    
                    # Strip forbidden columns out if present in source data
                    output_row.pop('priority_flag', None)
                    
                    writer.writerow(output_row)
                    
                except Exception as row_error:
                    # Capture and handle null/bad rows without crashing execution flow
                    print(f"Warning: Handled malformed input entry on row #{index}: {row_error}")
                    fallback_row = row.copy() if row else {}
                    fallback_row.update({
                        "complaint_id": row.get('complaint_id', f"ERR_{index}") if row else f"ERR_{index}",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Applied safe pipeline fallback execution because input fields were null or corrupted.",
                        "flag": "NEEDS_REVIEW"
                    })
                    writer.writerow(fallback_row)
                    
    except Exception as write_error:
        print(f"Error: Infrastructure failed to write target file dataset. Detail: {write_error}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
