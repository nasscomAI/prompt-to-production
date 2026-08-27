"""
UC-0A — Complaint Classifier
Build guided by agents.md and skills.md requirements.
"""
import argparse
import csv
import re

# Exact allowed categories from README.md
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

# Severity keywords specified in README.md that must trigger Urgent priority
SEVERITY_KEYWORDS = [
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


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: updated dict containing category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    location = (row.get("location") or "").strip()

    # Handle null / empty description
    if not description:
        out = dict(row)
        out["category"] = "Other"
        out["priority"] = "Low"
        out["reason"] = "No description provided in complaint record."
        out["flag"] = "NEEDS_REVIEW"
        return out

    desc_lower = description.lower()

    # 1. Check severity keywords for Urgent priority
    # Stem/variation matching for explicit severity keywords (e.g., injured, children, hospitalised, collapsed)
    is_urgent = False
    found_severity_word = None

    severity_patterns = [
        (r"\binjur(y|ed|ies)\b", "injury"),
        (r"\bchild(ren)?\b", "child"),
        (r"\bschool\b", "school"),
        (r"\bhospital(ised|ized)?\b", "hospital"),
        (r"\bambulance\b", "ambulance"),
        (r"\bfire\b", "fire"),
        (r"\bhazard\b", "hazard"),
        (r"\bfell\b", "fell"),
        (r"\bcollaps(e|ed|ing)\b", "collapse"),
    ]

    for pattern, keyword_label in severity_patterns:
        match = re.search(pattern, desc_lower)
        if match:
            is_urgent = True
            found_severity_word = match.group(0)
            break

    priority = "Urgent" if is_urgent else "Standard"

    # 2. Category matching based on domain signals present in description
    category_scores = {cat: 0 for cat in ALLOWED_CATEGORIES if cat != "Other"}

    # Signal mapping grounded in specification and complaint domain terms
    if re.search(r"\bpothole(s)?\b", desc_lower):
        category_scores["Pothole"] += 3

    if re.search(r"\b(flood(ed|ing)?|inundat(ed|ion)|waterlogging|waterlogged)\b", desc_lower):
        category_scores["Flooding"] += 3

    if re.search(r"\b(streetlight(s)?|lamp post|unlit|darkness|lighting)\b", desc_lower):
        category_scores["Streetlight"] += 3

    if re.search(r"\b(waste|garbage|trash|overflowing bins|dumped|debris)\b", desc_lower):
        category_scores["Waste"] += 3

    if re.search(r"\b(music|noise|loud|amplifiers|drilling|idling)\b", desc_lower):
        category_scores["Noise"] += 3

    if re.search(r"\b(drain|drainage|gutter|sewerage|stormwater)\b", desc_lower) and "blocked" in desc_lower:
        category_scores["Drain Blockage"] += 3
    elif re.search(r"\b(drain|drainage|gutter)\b", desc_lower):
        category_scores["Drain Blockage"] += 1

    if re.search(r"\b(heritage|historic|ancient|monument|museum)\b", desc_lower):
        category_scores["Heritage Damage"] += 3

    if re.search(r"\b(heat|heatwave|melting|temperature|temperatures|\d+°c|full sun)\b", desc_lower):
        category_scores["Heat Hazard"] += 3

    if re.search(r"\b(footpath|paving|cobblestones|tarmac|road surface|subsidence|cracked|sinking|buckled|road collapsed|tiles)\b", desc_lower):
        category_scores["Road Damage"] += 3

    # Sort categories by match score
    matching_cats = [cat for cat, score in category_scores.items() if score > 0]
    sorted_cats = sorted(matching_cats, key=lambda c: category_scores[c], reverse=True)

    category = "Other"
    flag = ""

    if len(sorted_cats) == 0:
        # No clear signal
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(sorted_cats) == 1:
        category = sorted_cats[0]
    else:
        # Check if top score is distinct
        top_score = category_scores[sorted_cats[0]]
        runner_up_score = category_scores[sorted_cats[1]]
        if top_score > runner_up_score:
            category = sorted_cats[0]
        else:
            # Overlapping / conflicting signals with equal top score -> ambiguous
            category = "Other"
            flag = "NEEDS_REVIEW"

    # 3. Generate grounded single-sentence reason citing specific words from description
    # Remove internal sentence-ending periods from description text for clean citation
    clean_desc_text = re.sub(r"\.(?=\s|$)", "", description).strip()
    words = clean_desc_text.split()
    citation_length = min(10, len(words))
    cited_excerpt = " ".join(words[:citation_length])

    if found_severity_word:
        reason = f"Description mentions '{found_severity_word}', triggering Urgent priority for {category.lower()} issue."
    else:
        reason = f"Complaint cites '{cited_excerpt}', classified under {category} with {priority} priority."

    out = dict(row)
    out["category"] = category
    out["priority"] = priority
    out["reason"] = reason
    out["flag"] = flag
    return out


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    rows = []
    fieldnames = []

    try:
        with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames or [])
            for row in reader:
                rows.append(row)
    except Exception as e:
        print(f"Error reading input file {input_path}: {e}")
        return

    # Ensure required output fields are present in header list
    output_fields = list(fieldnames)
    for req_field in ["category", "priority", "reason", "flag"]:
        if req_field not in output_fields:
            output_fields.append(req_field)

    classified_rows = []
    for row in rows:
        try:
            classified = classify_complaint(row)
            classified_rows.append(classified)
        except Exception as err:
            # Error resilience: produce fallback row on unexpected processing error
            fallback = dict(row)
            fallback["category"] = "Other"
            fallback["priority"] = "Low"
            fallback["reason"] = f"Processing error encountered: {err}"
            fallback["flag"] = "NEEDS_REVIEW"
            classified_rows.append(fallback)

    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(classified_rows)
    except Exception as e:
        print(f"Error writing output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

