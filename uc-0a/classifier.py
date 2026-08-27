"""
UC-0A — Complaint Classifier
Reads city complaint data from CSV files and classifies each complaint
into categories: sanitation, roads, water, electricity, others.
Uses rule-based keyword classification. Outputs structured JSON.
"""

import argparse
import csv
import json
import re
from pathlib import Path

# Keyword map: category -> list of keywords (case-insensitive)
CATEGORY_KEYWORDS = {
    "sanitation": [
        "garbage", "waste", "bin", "trash", "overflow", "dump", "dead animal",
        "smell", "garbage bins", "bulk waste", "landfill", "dengue", "mosquito"
    ],
    "roads": [
        "pothole", "road", "crack", "sink", "footpath", "manhole", "tiles",
        "surface", "repair", "potholes", "upturned", "broken"
    ],
    "water": [
        "flood", "drain", "water", "drainage", "flooded", "blocked drain",
        "stormwater", "floods"
    ],
    "electricity": [
        "streetlight", "streetlights", "light", "lights", "power", "electrical",
        "flickering", "sparking", "lights out", "dark"
    ],
}


def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint description using rule-based keyword matching.
    Returns dict with: category, reason, confidence.
    """
    if not description or not str(description).strip():
        return {
            "category": "others",
            "reason": "Empty description",
            "confidence": "low",
        }

    text = str(description).lower().strip()
    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                matches.append((category, kw))

    if not matches:
        return {
            "category": "others",
            "reason": "No matching keywords found",
            "confidence": "low",
        }

    # Count matches per category; strongest category wins
    cat_counts = {}
    cat_words = {}
    for cat, word in matches:
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        cat_words[cat] = cat_words.get(cat, []) + [word]

    best_category = max(cat_counts, key=cat_counts.get)
    reason_words = list(dict.fromkeys(cat_words[best_category]))
    reason = ", ".join(reason_words[:5])

    if cat_counts[best_category] >= 2:
        confidence = "high"
    elif cat_counts[best_category] == 1:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "category": best_category,
        "reason": reason,
        "confidence": confidence,
    }


def batch_classify(input_path: str, output_path: str, format_output: str = "json") -> list:
    """
    Read input CSV, classify each row, write results.
    Handles bad rows gracefully; produces partial output.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    errors = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        if "description" not in headers:
            raise ValueError("Input CSV must contain 'description' column")

        complaint_id_col = "complaint_id" if "complaint_id" in headers else None

        for i, row in enumerate(reader):
            try:
                desc = row.get("description", "")
                complaint_id = row.get(complaint_id_col or "", "") if complaint_id_col else f"row_{i + 2}"

                classification = classify_complaint(desc)
                out = {
                    "complaint_id": complaint_id,
                    "category": classification["category"],
                    "reason": classification["reason"],
                    "confidence": classification["confidence"],
                }
                results.append(out)
            except Exception as e:
                errors.append({"row": i + 2, "error": str(e)})

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format_output.lower() == "csv":
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "reason", "confidence"])
            writer.writeheader()
            writer.writerows(results)
    else:
        output_data = {"classifications": results, "total": len(results), "errors": errors}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

    # Print to console
    print("\n--- Classification Results ---\n")
    for r in results:
        print(f"  {r['complaint_id']}: {r['category']} ({r['confidence']}) — {r['reason']}")
    print(f"\n  Total: {len(results)} classified")
    if errors:
        print(f"  Errors: {len(errors)} row(s) skipped")
    print(f"\n  Results written to: {output_path}\n")

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results (JSON or CSV)")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format (default: json)")
    args = parser.parse_args()

    batch_classify(args.input, args.output, args.format)
    print("Done.")


if __name__ == "__main__":
    main()
