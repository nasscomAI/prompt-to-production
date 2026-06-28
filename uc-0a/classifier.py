"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and ambiguity flag
using weighted keyword matching against a fixed 10-category taxonomy.
"""
import argparse
import csv


# ── Fixed taxonomy — exact strings only ──────────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords that must trigger Urgent priority (case-insensitive)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword definitions: (keyword, weight)
# Higher weight → more specific to that category
CATEGORY_KEYWORDS = {
    "Pothole": [
        ("pothole", 5), ("crater", 4),
    ],
    "Flooding": [
        ("flood", 5), ("waterlog", 4), ("submerge", 3),
        ("knee-deep", 3), ("inundated", 3), ("stranded", 2),
        ("rain", 1), ("water", 1),
    ],
    "Streetlight": [
        ("streetlight", 5), ("street light", 5),
        ("lights out", 5), ("light out", 5),
        ("lamp", 3), ("unlit", 4), ("flickering", 3),
        ("sparking", 3), ("dark", 2), ("darkness", 3),
    ],
    "Waste": [
        ("garbage", 5), ("trash", 4), ("waste", 3),
        ("refuse", 3), ("dumped", 3), ("bin", 2),
        ("litter", 3), ("dead animal", 5), ("overflowing", 2),
        ("smell", 2), ("rubbish", 3),
    ],
    "Noise": [
        ("noise", 5), ("loud", 3), ("music", 4),
        ("midnight", 3), ("decibel", 4), ("wedding", 2),
        ("honking", 3), ("drilling", 3), ("amplifier", 3),
    ],
    "Road Damage": [
        ("road surface", 4), ("cracked", 3), ("sinking", 3),
        ("subsid", 4), ("tarmac", 3), ("paving", 3),
        ("divider", 3), ("footpath", 3), ("tile", 2),
        ("bridge approach", 3), ("cobblestone", 3), ("buckled", 3),
        ("collapsed", 3), ("road", 1),
    ],
    "Heritage Damage": [
        ("heritage", 5), ("ancient", 4), ("monument", 4),
        ("step well", 4), ("historical", 4),
    ],
    "Heat Hazard": [
        ("heat", 3), ("temperature", 3), ("melting", 4),
        ("\u00b0c", 3), ("heatwave", 4), ("sun", 1),
        ("burn", 1),
    ],
    "Drain Blockage": [
        ("drain", 4), ("sewer", 4), ("manhole", 4),
        ("blockage", 3), ("clogged", 4), ("blocked", 3),
    ],
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _score_categories(desc_lower: str):
    """Return {category: score} and {category: [matched_original_words]}."""
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}
    matched = {cat: [] for cat in CATEGORY_KEYWORDS}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw, weight in keywords:
            idx = desc_lower.find(kw.lower())
            if idx != -1:
                scores[cat] += weight
                matched[cat].append(kw)
    return scores, matched


def _build_reason(category: str, desc: str, matched_words: list) -> str:
    """Build a one-sentence reason citing specific words from the description."""
    if matched_words:
        # Deduplicate while preserving order
        unique = list(dict.fromkeys(matched_words))
        # Find original-case versions from the description
        desc_lower = desc.lower()
        cited = []
        for kw in unique[:5]:
            idx = desc_lower.find(kw.lower())
            if idx != -1:
                # Extend to full word boundary so stems cite the complete word
                end = idx + len(kw)
                while end < len(desc) and desc[end].isalpha():
                    end += 1
                cited.append(desc[idx:end])
            else:
                cited.append(kw)
        citation = ", ".join(f"'{w}'" for w in cited)
        return f"Classified as {category} because description cites {citation}."

    # Fallback: quote the first sentence of the description
    snippet = desc.split(".")[0].strip()
    if len(snippet) > 80:
        snippet = snippet[:77] + "..."
    return f'Classified as {category} based on description: "{snippet}".'


# ── Core skills ──────────────────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "")

    # Handle missing / empty description
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing or empty description.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = desc.lower()

    # ── Priority ─────────────────────────────────────────────────────────
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)

    try:
        days_open = int(row.get("days_open", 0))
    except (ValueError, TypeError):
        days_open = 0

    if is_urgent:
        priority = "Urgent"
    elif days_open >= 10:
        priority = "Standard"
    else:
        priority = "Low"

    # ── Category ─────────────────────────────────────────────────────────
    scores, matched = _score_categories(desc_lower)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    flag = ""

    if ranked[0][1] == 0:
        # No keywords matched any category
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = ranked[0][0]
        top_score = ranked[0][1]
        second_score = ranked[1][1] if len(ranked) > 1 else 0

        # Flag ambiguity: second-best category scores at least 60 % of the top
        if second_score >= 3 and second_score >= top_score * 0.6:
            flag = "NEEDS_REVIEW"

        # Specific cross-category ambiguity checks
        if scores["Drain Blockage"] >= 3 and scores["Flooding"] >= 3:
            flag = "NEEDS_REVIEW"
        if scores["Heritage Damage"] >= 3 and scores["Streetlight"] >= 3:
            flag = "NEEDS_REVIEW"

    # ── Reason ───────────────────────────────────────────────────────────
    reason = _build_reason(category, desc, matched.get(category, []))

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles missing files, bad rows, and null fields gracefully.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row_idx, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as exc:
                    # Graceful fallback — never crash on a single bad row
                    results.append({
                        "complaint_id": row.get(
                            "complaint_id", f"UNKNOWN_ROW_{row_idx}"
                        ),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Row processing failed: {exc}",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


# ── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
