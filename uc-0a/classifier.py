"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    # Allowed categories (exact strings)
    CATEGORIES = {
        "Pothole": [
            "pothole", "potholes", "hole in road", "hole in the road",
        ],
        "Flooding": ["flood", "flooded", "water logging", "waterlogged", "submerged", "inundat"],
        "Streetlight": ["streetlight", "street light", "lamp post", "streetlamp", "light not working"],
        "Waste": ["garbage", "waste", "rubbish", "trash", "dumping", "litter"],
        "Noise": ["noise", "loud", "honking", "construction noise", "music"],
        "Road Damage": ["road damage", "broken road", "uneven road", "crack", "cracked", "collapsed road"],
        "Heritage Damage": ["heritage", "monument", "statue", "vandal", "vandalism"],
        "Heat Hazard": ["heat", "heat hazard", "hot", "burn"],
        "Drain Blockage": ["drain", "blocked drain", "sewer", "sewage", "drainage", "manhole"],
    }

    SEVERITY_KEYWORDS = [
        "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
    ]

    LOW_KEYWORDS = ["low", "minor", "cosmetic"]

    # Helper
    def find_keywords(text, keywords):
        hits = []
        t = text.lower()
        for kw in keywords:
            if kw in t:
                hits.append(kw)
        return hits

    description = (row.get("description") or row.get("desc") or "")
    if description is None:
        description = ""
    description = description.strip()

    result = {
        "category": "Other",
        "priority": "Standard",
        "reason": "",
        "flag": "",
    }

    if not description:
        result["reason"] = "Missing description; cannot classify."
        result["flag"] = "NEEDS_REVIEW"
        return result

    # Find category matches
    matched_categories = []
    matched_terms = {}
    for cat, kws in CATEGORIES.items():
        hits = []
        for kw in kws:
            if kw in description.lower():
                hits.append(kw)
        if hits:
            matched_categories.append(cat)
            matched_terms[cat] = hits

    # Determine priority
    sev_hits = find_keywords(description, SEVERITY_KEYWORDS)
    low_hits = find_keywords(description, LOW_KEYWORDS)
    if sev_hits:
        result["priority"] = "Urgent"
    elif low_hits:
        result["priority"] = "Low"
    else:
        result["priority"] = "Standard"

    # Decide on category and flag
    if len(matched_categories) == 1:
        cat = matched_categories[0]
        result["category"] = cat
        # reason must cite specific words
        cited = matched_terms.get(cat, []) + sev_hits
        cited = list(dict.fromkeys(cited))
        if cited:
            quoted = ", ".join([f'"{s}"' for s in cited])
            result["reason"] = f"Mentions {quoted} in description."
        else:
            result["reason"] = "Matched category by pattern but no explicit keyword captured."
        result["flag"] = ""
    elif len(matched_categories) > 1:
        # Ambiguous between multiple categories
        result["category"] = "Other"
        # create reason listing categories and sample terms
        parts = []
        for c in matched_categories:
            parts.append(f"{c} (found {', '.join([f'\"{t}\"' for t in matched_terms.get(c,[])])})")
        result["reason"] = "Ambiguous: matches " + "; ".join(parts)
        result["flag"] = "NEEDS_REVIEW"
    else:
        # No category matched
        result["category"] = "Other"
        # mention any severity keywords if present
        if sev_hits:
            quoted = ", ".join([f'"{s}"' for s in sev_hits])
            result["reason"] = f"No category keywords matched; severity words present: {quoted}."
            result["flag"] = "NEEDS_REVIEW"
        else:
            result["reason"] = "No category keywords matched in description."
            result["flag"] = "NEEDS_REVIEW"

    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    total = 0
    classified = 0
    needs_review = 0
    errors = 0

    with open(input_path, newline='', encoding='utf-8') as infp:
        reader = csv.DictReader(infp)
        input_fieldnames = reader.fieldnames or []
        out_fieldnames = list(input_fieldnames) + ["category", "priority", "reason", "flag"]

        rows_out = []
        for row in reader:
            total += 1
            try:
                res = classify_complaint(row)
                out_row = dict(row)
                out_row["category"] = res.get("category", "Other")
                out_row["priority"] = res.get("priority", "Standard")
                out_row["reason"] = res.get("reason", "")
                out_row["flag"] = res.get("flag", "")

                if out_row["flag"] == "NEEDS_REVIEW":
                    needs_review += 1
                else:
                    classified += 1

                rows_out.append(out_row)
            except Exception as e:
                errors += 1
                err_row = dict(row)
                err_row["category"] = "Other"
                err_row["priority"] = "Standard"
                err_row["reason"] = f"Error classifying row: {e}"
                err_row["flag"] = "NEEDS_REVIEW"
                rows_out.append(err_row)

    # Write output CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as outfp:
        writer = csv.DictWriter(outfp, fieldnames=out_fieldnames)
        writer.writeheader()
        for r in rows_out:
            writer.writerow(r)

    summary = {
        "total": total,
        "classified": classified,
        "needs_review": needs_review,
        "errors": errors,
    }
    print(f"Processed {total} rows — classified: {classified}, needs_review: {needs_review}, errors: {errors}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
