"""
UC-0A — Complaint Classifier
Implements RICE framework from agents.md + skills.md with strict enforcement.

ENFORCEMENT RULES:
1. Category: exactly one of 10 allowed values or "Other"
2. Priority: "Urgent" if severity keywords present, else "Standard" or "Low"
3. Reason: one sentence citing 2-3 actual words from description
4. Flag: "NEEDS_REVIEW" iff ambiguous (2+ categories equally plausible)
"""

import argparse
import csv
import re
from typing import Dict, List, Tuple
from pathlib import Path

# ============================================================================
# ENFORCEMENT CONSTANTS
# ============================================================================

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
    "Other",
}

SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Category detection patterns (order matters: most specific first)
CATEGORY_PATTERNS = [
    ("Pothole", [r"\bpothole", r"\bhole\b", r"\brut", r"\btyre\s+damage"]),
    ("Flooding", [r"\bflood", r"\bwater\b", r"\bwaterslogging", r"\bstagnant\s+water", r"\binundated", r"\bstranded"]),
    ("Drain Blockage", [r"\bdrain.*block", r"\bblocked\s+drain", r"\bclogged\s+drain", r"\bsewer", r"\bstorm\s+water", r"\bmanhole"]),
    ("Streetlight", [r"\bstreetlight", r"\blight.*out", r"\blamp.*out", r"\bstreet\s+lamp", r"\belectric", r"\bflickering", r"\bsparking"]),
    ("Road Damage", [r"\broad.*crack", r"\bcracked\s+road", r"\bsinking\b", r"\basphalt", r"\brepair.*road", r"\bpave", r"\bfootpath", r"\bpath\s+tiles", r"\bupturned"]),
    ("Waste", [r"\bgarbage", r"\bwaste", r"\brubble", r"\bdebris", r"\btrash", r"\bdumped"]),
    ("Noise", [r"\bnoise", r"\bmusic\b", r"\bsound", r"\bloud"]),
    ("Heritage Damage", [r"\bheritage", r"\bhistoric", r"\bmonument", r"\barchaeo", r"\bold\s+city"]),
    ("Heat Hazard", [r"\bheat\s+hazard", r"\bheat\s+stress", r"\btemperature"]),
]


def extract_keywords_from_desc(desc: str) -> List[str]:
    """Extract 2-3 key phrases from description for reason field."""
    words = desc.lower().split()
    # Filter out common stop words
    stop_words = {"the", "a", "an", "and", "or", "is", "are", "of", "in", "at", "on", "to"}
    keywords = [w.strip(".,!?;:") for w in words if w.strip(".,!?;:") not in stop_words and len(w) > 3]
    return keywords[:3] if len(keywords) >= 2 else keywords


def find_severity_keyword(desc: str) -> str:
    """Check if description contains any severity keyword (case-insensitive, whole word)."""
    desc_lower = desc.lower()
    for keyword in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", desc_lower):
            return keyword
    return None


def detect_categories(desc: str) -> List[Tuple[str, float]]:
    """
    Detect all matching categories with confidence score.
    Returns: list of (category, confidence) sorted by confidence descending.
    """
    desc_lower = desc.lower()
    matches = []
    
    for category, patterns in CATEGORY_PATTERNS:
        match_count = 0
        for pattern in patterns:
            if re.search(pattern, desc_lower):
                match_count += 1
        if match_count > 0:
            confidence = match_count / len(patterns)  # fraction of patterns matched
            matches.append((category, confidence))
    
    # Sort by confidence descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using RICE enforcement rules.
    
    Input: dict with keys "complaint_id" (optional), "description" (required)
    Output: dict with keys "complaint_id", "category", "priority", "reason", "flag"
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    
    # ========================================================================
    # ERROR HANDLING: Empty or insufficient description
    # ========================================================================
    if not description or len(description) < 5:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    # ========================================================================
    # RULE 1 & 4: Detect categories + ambiguity flagging
    # ========================================================================
    matches = detect_categories(description)
    
    if not matches:
        # No category detected -> use "Other"
        category = "Other"
        confidence = 0.0
        flag = "NEEDS_REVIEW"
    else:
        # Take highest confidence category
        category, confidence = matches[0]
        
        # Check for ambiguity: if top two categories have similar confidence,
        # or if multiple categories have high confidence, flag NEEDS_REVIEW
        flag = ""
        if len(matches) >= 2:
            top_conf = matches[0][1]
            second_conf = matches[1][1]
            # If scores are close (within 20% relative difference), it's ambiguous
            if second_conf > 0 and (top_conf - second_conf) / top_conf < 0.2:
                flag = "NEEDS_REVIEW"
        
        # Also flag if confidence is very low (< 0.4)
        if confidence < 0.4:
            flag = "NEEDS_REVIEW"
    
    # ========================================================================
    # RULE 2: Determine priority based on severity keywords
    # ========================================================================
    severity_keyword = find_severity_keyword(description)
    if severity_keyword:
        priority = "Urgent"
    else:
        priority = "Standard"
    
    # ========================================================================
    # RULE 3: Generate reason citing specific words from description
    # ========================================================================
    keywords = extract_keywords_from_desc(description)
    
    if keywords:
        keyword_str = ", ".join(f'"{kw}"' for kw in keywords)
        reason = f"{category} because description mentions {keyword_str}."
    else:
        reason = f"Classified as {category} based on complaint description."
    
    # Enforce: reason is one sentence
    reason = reason.split(".")[0] + "."
    
    # ========================================================================
    # ENFORCEMENT CHECKS (sanity checks, should always pass)
    # ========================================================================
    assert category in ALLOWED_CATEGORIES, f"Invalid category: {category}"
    assert priority in {"Urgent", "Standard", "Low"}, f"Invalid priority: {priority}"
    assert flag in {"NEEDS_REVIEW", ""}, f"Invalid flag: {flag}"
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row using classify_complaint, write output CSV.
    Handles errors gracefully: logs errors, continues processing, writes all rows.
    
    Input CSV required columns: "description"
    Optional: "complaint_id" (auto-generates if missing)
    
    Output CSV columns: "complaint_id", "category", "priority", "reason", "flag"
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # ========================================================================
    # ERROR HANDLING: File validation
    # ========================================================================
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # READ INPUT CSV
    # ========================================================================
    rows_processed = 0
    rows_flagged = 0
    errors = []
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            if reader.fieldnames is None or "description" not in reader.fieldnames:
                raise ValueError("Input CSV must contain 'description' column")
            
            for row_idx, row in enumerate(reader, start=1):
                try:
                    # Auto-generate complaint_id if missing
                    if "complaint_id" not in row or not row["complaint_id"]:
                        row["complaint_id"] = f"row_{row_idx}"
                    
                    # Classify this row
                    classified = classify_complaint(row)
                    results.append(classified)
                    rows_processed += 1
                    
                    if classified["flag"] == "NEEDS_REVIEW":
                        rows_flagged += 1
                
                except Exception as e:
                    # Log error but continue processing
                    error_msg = f"Row {row_idx}: {str(e)}"
                    errors.append(error_msg)
                    
                    # Write partial row with safe defaults
                    results.append({
                        "complaint_id": row.get("complaint_id", f"row_{row_idx}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Classification failed due to error.",
                        "flag": "NEEDS_REVIEW"
                    })
                    rows_processed += 1
                    rows_flagged += 1
    
    except Exception as e:
        raise RuntimeError(f"Failed to read input CSV: {str(e)}")
    
    # ========================================================================
    # WRITE OUTPUT CSV
    # ========================================================================
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    
    except Exception as e:
        raise RuntimeError(f"Failed to write output CSV: {str(e)}")
    
    # ========================================================================
    # REPORT
    # ========================================================================
    print(f"Processed: {rows_processed} rows")
    print(f"Flagged for review: {rows_flagged} rows")
    print(f"Errors encountered: {len(errors)}")
    if errors:
        for err in errors[:5]:  # Print first 5 errors
            print(f"  - {err}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"✓ Done.")
