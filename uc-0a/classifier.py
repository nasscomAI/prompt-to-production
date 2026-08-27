"""
UC-0A — Complaint Classifier
Classifies civic complaints into predefined categories and priority levels.
Enforcement: fixed taxonomy, severity keywords → Urgent, cited reasons, ambiguity flagging.
"""
import argparse
import csv
import re
import sys

# Fixed taxonomy — no variations allowed
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that must trigger Urgent priority (case-insensitive)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category detection patterns — ordered by specificity
CATEGORY_PATTERNS = {
    "Pothole": [r"\bpothole\b", r"\bpotholes\b"],
    "Flooding": [r"\bflood\w*\b", r"\bwater\s*log\w*\b", r"\bsubmerg\w*\b", r"\bstranded\b", r"\bknee.?deep\b"],
    "Streetlight": [r"\bstreetlight\b", r"\bstreet\s*light\b", r"\blight\w*\s+out\b", r"\blights?\s+out\b", r"\bflickering\b", r"\bdark\s+at\s+night\b", r"\blighting\b"],
    "Waste": [r"\bgarbage\b", r"\bwaste\b", r"\brubbish\b", r"\boverflowing\b", r"\bdead\s+animal\b", r"\btrash\b", r"\bdumped\b", r"\bdump\b"],
    "Noise": [r"\bnoise\b", r"\bmusic\s+past\b", r"\bloud\b", r"\bmidnight\b", r"\bnuisance\b"],
    "Road Damage": [r"\broad\s+surface\b", r"\bcrack\w*\b", r"\bsinking\b", r"\bbroken\b.*\b(footpath|pavement|tiles?)\b", r"\bupturned\b", r"\bfootpath\b.*\b(broken|crack|damage)\b"],
    "Heritage Damage": [r"\bheritage\b", r"\bhistoric\w*\b", r"\bmonument\b"],
    "Heat Hazard": [r"\bheat\b", r"\btemperature\b", r"\bsunstroke\b"],
    "Drain Blockage": [r"\bdrain\s*block\w*\b", r"\bmanhole\b", r"\bdrain\w*\b.*\bblock\w*\b", r"\bsewer\b", r"\bblocked\s+drain\b"],
}


def has_severity_keyword(description: str) -> tuple:
    """Check if description contains any severity keyword. Returns (bool, matched_keyword)."""
    desc_lower = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r"\b" + keyword + r"\b", desc_lower):
            return True, keyword
    return False, None


def determine_category(description: str) -> tuple:
    """
    Determine complaint category from description.
    Returns (category, confidence, matched_terms).
    confidence: 'high' if one clear match, 'ambiguous' if multiple matches.
    """
    desc_lower = description.lower()
    matches = {}

    for category, patterns in CATEGORY_PATTERNS.items():
        matched_terms = []
        for pattern in patterns:
            found = re.findall(pattern, desc_lower)
            if found:
                matched_terms.extend(found)
        if matched_terms:
            matches[category] = matched_terms

    if len(matches) == 0:
        return "Other", "none", []
    elif len(matches) == 1:
        cat = list(matches.keys())[0]
        return cat, "high", matches[cat]
    else:
        # Multiple matches — pick the one with the most pattern hits
        sorted_matches = sorted(matches.items(), key=lambda x: len(x[1]), reverse=True)
        best_cat = sorted_matches[0][0]
        # If top two are close, mark as ambiguous
        if len(sorted_matches) > 1 and len(sorted_matches[0][1]) == len(sorted_matches[1][1]):
            return best_cat, "ambiguous", matches[best_cat]
        return best_cat, "high", matches[best_cat]


def determine_priority(description: str, category: str) -> tuple:
    """
    Determine priority level.
    Returns (priority, reason_fragment).
    """
    is_severe, keyword = has_severity_keyword(description)
    if is_severe:
        return "Urgent", f"contains severity keyword '{keyword}'"

    # Active safety/infrastructure issues default to Standard
    # Cosmetic or non-safety issues can be Low
    low_indicators = [r"\bcosmetic\b", r"\baesthetic\b", r"\bminor\b.*\binconvenience\b"]
    desc_lower = description.lower()
    for pattern in low_indicators:
        if re.search(pattern, desc_lower):
            return "Low", "cosmetic/non-safety issue"

    return "Standard", "active infrastructure issue"


def build_reason(category: str, priority: str, matched_terms: list, priority_reason: str, description: str) -> str:
    """Build a one-sentence reason citing specific words from the description."""
    if matched_terms:
        cited = ", ".join(set(matched_terms[:3]))
        return f"Classified as {category} ({priority}) based on description containing: {cited}; {priority_reason}."
    else:
        # For 'Other' category — cite first few meaningful words
        words = description.split()[:5]
        snippet = " ".join(words)
        return f"Classified as {category} ({priority}): no clear category match from description '{snippet}...'; {priority_reason}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle empty/missing description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    # Determine category
    category, confidence, matched_terms = determine_category(description)

    # Determine priority
    priority, priority_reason = determine_priority(description, category)

    # Build reason
    reason = build_reason(category, priority, matched_terms, priority_reason, description)

    # Set flag for ambiguous cases
    flag = "NEEDS_REVIEW" if confidence == "ambiguous" or confidence == "none" else ""

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
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot read input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    error_count = 0

    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            error_count += 1
            results.append({
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {e}",
                "flag": "NEEDS_REVIEW"
            })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    print(f"Classified {len(results)} complaints ({error_count} errors).")
    categories = {}
    priorities = {}
    for r in results:
        categories[r["category"]] = categories.get(r["category"], 0) + 1
        priorities[r["priority"]] = priorities.get(r["priority"], 0) + 1
    print(f"Categories: {dict(sorted(categories.items()))}")
    print(f"Priorities: {dict(sorted(priorities.items()))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
