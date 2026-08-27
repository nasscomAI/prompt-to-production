"""
UC-0A — Complaint Classifier
Implements RICE framework for complaint classification with severity detection and taxonomy enforcement.
"""
import argparse
import csv
import os
import sys
from pathlib import Path

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Classification Schema
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]


def detect_file_format(file_path: str) -> str:
    """
    Detect input file format by extension.
    Returns: "csv" or "xlsx"
    """
    ext = Path(file_path).suffix.lower()
    if ext == ".csv":
        return "csv"
    elif ext == ".xlsx":
        if not HAS_PANDAS:
            raise ImportError("pandas required for Excel support. Install: pip install pandas openpyxl")
        return "xlsx"
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .csv or .xlsx")


def detect_severity_keywords(description: str) -> list:
    """
    Scan complaint description for severity keywords.
    Returns: list of keywords found (case-insensitive)
    """
    if not description or not isinstance(description, str):
        return []
    
    desc_lower = description.lower()
    found = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    return found


def validate_taxonomy(category: str) -> tuple:
    """
    Validate category against allowed taxonomy.
    Returns: (is_valid: bool, canonical_category: str or None)
    """
    if not isinstance(category, str):
        return (False, None)
    
    if category in ALLOWED_CATEGORIES:
        return (True, category)
    
    return (False, None)


def extract_reason(description: str, category: str, severity_keywords: list) -> str:
    """
    Generate justification reason citing specific words from description.
    """
    if not description:
        return "No description provided."
    
    reason_parts = []
    
    # Add severity keyword reference if present
    if severity_keywords:
        kw_str = ", ".join(severity_keywords[:2])  # Cite first 2 keywords
        reason_parts.append(f"Description mentions {kw_str}.")
    
    # Add category-specific reference
    category_keywords = {
        "Pothole": ["pothole", "hole", "pit", "road"],
        "Flooding": ["flood", "water", "waterlogging", "rain"],
        "Streetlight": ["light", "streetlight", "lamp", "dark"],
        "Waste": ["waste", "garbage", "trash", "rubbish"],
        "Noise": ["noise", "sound", "loud", "noise"],
        "Road Damage": ["damage", "road", "pavement", "surface"],
        "Heritage Damage": ["heritage", "historic", "monument", "old"],
        "Heat Hazard": ["heat", "hot", "temperature", "hazard"],
        "Drain Blockage": ["drain", "blockage", "clogged", "sewage"],
    }
    
    if category in category_keywords:
        for kw in category_keywords[category]:
            if kw.lower() in description.lower():
                reason_parts.append(f"Found '{kw}' in description.")
                break
    
    # Construct final reason
    if reason_parts:
        reason = " ".join(reason_parts)
    else:
        reason = f"Classified as {category} based on complaint description."
    
    # Ensure exactly one sentence (add period if missing)
    if not reason.endswith("."):
        reason += "."
    
    return reason[:200]  # Truncate to 200 chars


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Input: dict with keys complaint_id, description, [other fields]
    Output: dict with keys complaint_id, category, priority, reason, flag
    
    Enforces RICE rules:
    - Category must be exact taxonomy match
    - Priority=Urgent if severity keyword present
    - Reason must cite specific description words
    - Flag=NEEDS_REVIEW if ambiguous or error
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    # Initialize output
    result = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": "",
        "flag": ""
    }
    
    # Error handling: missing description
    if not description or not isinstance(description, str):
        result["category"] = "Other"
        result["priority"] = "Standard"
        result["reason"] = "No description provided."
        result["flag"] = "NEEDS_REVIEW"
        return result
    
    # Detect severity keywords → Priority determination
    severity_kws = detect_severity_keywords(description)
    result["priority"] = "Urgent" if severity_kws else "Standard"
    
    # Simple category detection (rule-based for now)
    # This should be enhanced with LLM calls in production
    description_lower = description.lower()
    
    category_rules = {
        "Pothole": ["pothole", "hole", "pit"],
        "Flooding": ["flood", "waterlog", "water accumul"],
        "Streetlight": ["streetlight", "lamp", "lighting", "dark", "light"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "litter"],
        "Noise": ["noise", "loud", "sound"],
        "Road Damage": ["road damage", "pavement", "cracked", "surface damage"],
        "Heritage Damage": ["heritage", "historic", "monument", "old building"],
        "Heat Hazard": ["heat", "temperature", "hot", "hazard"],
        "Drain Blockage": ["drain", "blockage", "clogged", "sewage"],
    }
    
    # Determine category
    matched_categories = []
    for cat, keywords in category_rules.items():
        for kw in keywords:
            if kw.lower() in description_lower:
                matched_categories.append(cat)
                break
    
    if len(matched_categories) == 1:
        result["category"] = matched_categories[0]
    elif len(matched_categories) > 1:
        # Ambiguous: multiple categories match
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
    else:
        # No category matched
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
    
    # Generate reason
    result["reason"] = extract_reason(description, result["category"], severity_kws)
    
    return result


def read_input_file(input_path: str) -> list:
    """
    Read input file (CSV or Excel) and return list of dicts.
    """
    file_format = detect_file_format(input_path)
    
    if file_format == "csv":
        rows = []
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {input_path}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
    
    elif file_format == "xlsx":
        try:
            df = pd.read_excel(input_path)
            rows = df.to_dict("records")
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {input_path}")
        except Exception as e:
            raise IOError(f"Error reading Excel file: {e}")
    
    return rows


def write_output_file(results: list, output_path: str, output_format: str = None):
    """
    Write results to output file (CSV or Excel).
    If output_format is None, auto-detect from output_path extension.
    """
    if output_format is None:
        output_format = detect_file_format(output_path)
    
    if not results:
        # Write empty file with headers
        results = [{
            "complaint_id": "", "category": "", "priority": "", 
            "reason": "", "flag": ""
        }]
    
    if output_format == "csv":
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
                writer.writeheader()
                writer.writerows(results)
        except IOError as e:
            raise IOError(f"Cannot write to output file: {e}")
    
    elif output_format == "xlsx":
        try:
            df = pd.DataFrame(results)
            df.to_excel(output_path, index=False, engine="openpyxl")
            
            # Optional: Format Excel (bold headers, auto-width)
            try:
                from openpyxl import load_workbook
                from openpyxl.styles import Font
                wb = load_workbook(output_path)
                ws = wb.active
                for cell in ws[1]:
                    cell.font = Font(bold=True)
                wb.save(output_path)
            except Exception:
                pass  # Formatting is optional
        except IOError as e:
            raise IOError(f"Cannot write to output file: {e}")


def batch_classify(input_path: str, output_path: str, output_format: str = None):
    """
    Read input file, classify each row, write results.
    
    Enforces:
    - All output categories are valid
    - No crash on bad rows (flag them instead)
    - Produces output even if some rows fail
    """
    print(f"Reading input from: {input_path}")
    
    # Read input
    rows = read_input_file(input_path)
    print(f"Loaded {len(rows)} complaint rows.")
    
    if len(rows) == 0:
        print("Warning: input file has no rows.")
    
    # Classify each row
    results = []
    error_count = 0
    
    for idx, row in enumerate(rows):
        try:
            result = classify_complaint(row)
            
            # Validate output category
            is_valid, canonical = validate_taxonomy(result["category"])
            if not is_valid:
                result["flag"] = "NEEDS_REVIEW"
                result["category"] = "Other"
                error_count += 1
            
            results.append(result)
        except Exception as e:
            print(f"Error classifying row {idx}: {e}")
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification failed: {str(e)[:50]}",
                "flag": "NEEDS_REVIEW"
            })
            error_count += 1
    
    # Write output
    print(f"Writing {len(results)} results to: {output_path}")
    write_output_file(results, output_path, output_format)
    
    # Summary
    print(f"\n=== Classification Complete ===")
    print(f"Total rows: {len(rows)}")
    print(f"Errors/Flags: {error_count}")
    print(f"Output written to: {output_path}")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv or .xlsx")
    parser.add_argument("--output", required=True, help="Path to write results CSV or .xlsx")
    parser.add_argument("--output-format", choices=["csv", "xlsx"], default=None, 
                        help="Output format (auto-detect if not specified)")
    args = parser.parse_args()
    
    try:
        batch_classify(args.input, args.output, args.output_format)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
