"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re
from typing import Dict, Tuple, List

ALLOWED_CATEGORIES = [
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

URGENT_KEYWORDS = [
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

LOW_HINTS = [
    "request",
    "please",
    "minor",
    "small",
    "sometimes",
    "repair",
]

def _finalize_reason(reason: str) -> str:
    """
    Enforce a single-sentence output by removing internal periods
    and ensuring exactly one trailing '.'.
    """
    # Remove all '.' from the middle of the reason (quoted description may contain periods).
    reason = reason.replace(".", "")
    reason = reason.strip()
    # Remove trailing punctuation other than periods (defensive; we always add a final '.').
    reason = re.sub(r"[!?]+$", "", reason).strip()
    return reason + "."


def _contains_any_keyword(text_lower: str, keywords: List[str]) -> Tuple[bool, str]:
    """
    Returns (matched, matched_keyword_substring).
    matched_keyword_substring is the first keyword found (exact keyword string from the list).
    """
    for kw in keywords:
        if kw in text_lower:
            return True, kw
    return False, ""


def _extract_first_evidence(text: str, text_lower: str, phrases: List[str]) -> str:
    """
    Try to return one exact substring from the original text that justifies a classification.
    Falls back to the first word if no phrase match is found.
    """
    for phrase in phrases:
        if phrase in text_lower:
            # Find exact indices in original string.
            # We do a case-insensitive scan and return the matched slice.
            idx = text_lower.find(phrase)
            if idx != -1:
                return text[idx : idx + len(phrase)]
    # Fallback: first non-empty word
    m = re.search(r"[A-Za-z0-9][A-Za-z0-9\-\']*", text)
    return m.group(0) if m else ""


def _score_categories(description_lower: str) -> Dict[str, int]:
    """
    Simple keyword-based scoring for category prediction.
    Higher score means more confident match.
    """
    category_keywords: Dict[str, List[str]] = {
        "Pothole": ["pothole", "potholes", "tyre damage", "wheel damage", "road hole"],
        "Flooding": ["flood", "flooded", "waterlogged", "waterlogging", "knee-deep", "commuters stranded", "submerged"],
        "Streetlight": ["streetlight", "street lights", "lamp", "lights out", "flickering", "spark", "dark at night"],
        "Waste": ["garbage", "trash", "waste", "dumped", "bins", "bin", "smell", "dumping", "renovation dumped"],
        "Noise": ["noise", "loud", "music", "past midnight", "honk", "horn", "sirens"],
        "Road Damage": ["cracked", "sinking", "road surface cracked", "cracks", "broken road", "uneven", "uplifted", "upturned", "road damage"],
        "Heritage Damage": ["heritage", "historic", "monument", "temple", "historic street"],
        "Heat Hazard": ["heat", "overheating", "hot", "temperature", "burn"],
        "Drain Blockage": ["drain", "blocked drain", "clogged", "gutter", "manhole", "manhole cover", "blocked", "underpass flooded"],
    }

    scores: Dict[str, int] = {}
    for cat, keywords in category_keywords.items():
        score = 0
        for kw in keywords:
            if kw in description_lower:
                score += 1
        if score > 0:
            scores[cat] = score
    return scores


def _choose_category(description: str) -> Tuple[str, str]:
    """
    Returns (category, flag).
    flag is NEEDS_REVIEW only when the category is ambiguous.
    """
    description_lower = description.lower()
    scores = _score_categories(description_lower)

    if not scores:
        return "Other", "NEEDS_REVIEW"

    # Find top categories
    sorted_cats = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_cat, top_score = sorted_cats[0]

    if len(sorted_cats) == 1:
        return top_cat, ""

    # If multiple categories match similarly, mark ambiguous
    second_score = sorted_cats[1][1]
    if top_score < second_score + 1:
        return "Other", "NEEDS_REVIEW"

    return top_cat, ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    try:
        complaint_id = (row or {}).get("complaint_id", "") or (row or {}).get("id", "")
        description = (row or {}).get("description", "")
        if description is None:
            description = ""
        description = str(description).strip()

        if not description:
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Standard",
                "reason": "Description missing",
                "flag": "NEEDS_REVIEW",
            }

        description_lower = description.lower()

        # Category selection with ambiguity handling
        category, category_flag = _choose_category(description)
        if category not in ALLOWED_CATEGORIES:
            category = "Other"
            category_flag = "NEEDS_REVIEW"

        # Priority selection
        urgent_match, urgent_kw = _contains_any_keyword(description_lower, URGENT_KEYWORDS)
        if urgent_match:
            priority = "Urgent"
        else:
            low_match, low_kw = _contains_any_keyword(description_lower, LOW_HINTS)
            priority = "Low" if low_match else "Standard"

        # Build a one-sentence reason with evidence from the description
        evidence_category = ""
        if category != "Other":
            # Evidence is based on the category-specific keyword list.
            # Use a compact list for evidence extraction (keeps reasons deterministic).
            evidence_map = {
                "Pothole": ["pothole", "potholes"],
                "Flooding": ["flood", "waterlogged", "waterlogging"],
                "Streetlight": ["streetlight", "street lights", "lamp", "lights out", "flickering"],
                "Waste": ["garbage", "trash", "waste", "dumped", "bins"],
                "Noise": ["noise", "music", "loud"],
                "Road Damage": ["cracked", "sinking", "upturned", "road surface cracked"],
                "Heritage Damage": ["heritage", "historic", "monument", "temple"],
                "Heat Hazard": ["heat", "overheating", "hot"],
                "Drain Blockage": ["drain", "manhole", "gutter", "blocked drain", "clogged"],
            }
            evidence_category = _extract_first_evidence(
                description,
                description_lower,
                evidence_map.get(category, []),
            )

        if priority == "Urgent":
            evidence_priority = urgent_kw
        elif priority == "Low":
            evidence_priority = low_kw
        else:
            evidence_priority = ""

        # Ensure exactly one sentence (one terminal period)
        if category_flag == "NEEDS_REVIEW" or category == "Other":
            # Cite some exact words from the description to justify Other+review.
            first_words = re.sub(r"\s+", " ", description).strip()
            if len(first_words) > 60:
                first_words = first_words[:60]
            reason = f'Cannot confidently classify from description words "{first_words}"; set category Other and flag NEEDS_REVIEW.'
            reason = _finalize_reason(reason)
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": priority,
                "reason": reason,
                "flag": "NEEDS_REVIEW",
            }

        if priority == "Urgent":
            reason = (
                f'Category {category} because the description mentions "{evidence_category}" '
                f'and priority is Urgent due to "{evidence_priority}".'
            )
        elif priority == "Low":
            reason = (
                f'Category {category} because the description mentions "{evidence_category}" '
                f'and priority is Low due to the maintenance/request wording "{evidence_priority}".'
            )
        else:
            # Standard: still cite category evidence to satisfy the "cite specific words" rule.
            reason = f'Category {category} because the description mentions "{evidence_category}", with priority Standard.'

        reason = _finalize_reason(reason)
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": "",
        }
    except Exception:
        # Never crash the batch run; fall back safely.
        complaint_id = ""
        try:
            complaint_id = (row or {}).get("complaint_id", "") or (row or {}).get("id", "")
        except Exception:
            complaint_id = ""
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Row invalid or ambiguous",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(input_path, "r", encoding="utf-8", newline="") as f_in:
        reader = csv.DictReader(f_in)
        with open(output_path, "w", encoding="utf-8", newline="") as f_out:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception:
                    # Defensive fallback for unexpected rows
                    result = {
                        "complaint_id": (row or {}).get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Row invalid or ambiguous",
                        "flag": "NEEDS_REVIEW",
                    }
                writer.writerow(
                    {
                        "complaint_id": result.get("complaint_id", ""),
                        "category": result.get("category", "Other"),
                        "priority": result.get("priority", "Standard"),
                        "reason": result.get("reason", "Row invalid or ambiguous"),
                        "flag": result.get("flag", ""),
                    }
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
