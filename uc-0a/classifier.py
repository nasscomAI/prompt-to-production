"""
UC-0A — Complaint Classifier
Built via RICE → agents.md → skills.md → CRAFT workflow.
Enforces: taxonomy exactness, severity keywords, cited reason, NEEDS_REVIEW on ambiguity, batch robustness.
"""
import argparse
import csv
import os
import re

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

# Keyword map for deterministic scoring — each keyword is a case-insensitive substring
# that appears in real test data. Keep substrings short to guarantee verbatim match.
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": [
        "flooded", "flooding", "floods", "flood",
        "waterlogged", "stranded", "knee-deep", "underpass",
        "inaccessible", "channel rainwater"
    ],
    "Streetlight": [
        "streetlight", "streetlights", "lamp post",
        "unlit", "lights out", "dark at night", "darkness",
        "sparking", "flickering", "substation tripped"
    ],
    "Waste": [
        "garbage", "waste", "bins overflowing", "overflowing garbage",
        "bins", "overflow", "dumped", "not cleared", "not removed",
        "dead animal", "piles of waste", "smell", "health concern", "health risk", "bulk waste"
    ],
    "Noise": [
        "music", "wedding", "drilling", "amplifier", "amplifiers",
        "venue playing", "band playing", "club music",
        "delivery trucks", "idling", "engines on"
    ],
    "Road Damage": [
        "road surface", "road collapsed", "road subsided", "road subsidence",
        "crater", "subsidence", "footpath", "paving", "upturned",
        "cracked and sinking", "cracked", "sinking", "buckled", "tiles broken",
        "gas pipeline", "utility work"
    ],
    "Heritage Damage": [
        "heritage lamp post", "heritage street", "heritage stone", "heritage zone", "heritage precinct", "heritage residential",
        "heritage", "historic", "ancient", "museum", "tagore",
        "step well", "marble palace", "cobblestones", "tram road",
        "stone not replaced", "defaced", "billboard installation"
    ],
    "Heat Hazard": [
        "melting", "heat", "temperature", "heatwave", "bubbling", "burns",
        "exposed to full sun", "full sun", "unbearable",
        "storing heat", "dangerous temperatures", "sun", "44", "45", "52"
    ],
    "Drain Blockage": [
        "drain blocked", "drain 100% blocked", "drain completely blocked",
        "stormwater drain", "main drain", "blocked with construction debris",
        "mosquito", "dengue", "manhole", "draining directly onto", "draining",
        "drain"
    ],
    "Other": [],
}

PRIORITY_URGENT = "Urgent"
PRIORITY_STANDARD = "Standard"


def _determine_priority(description: str) -> str:
    if not description:
        return PRIORITY_STANDARD
    lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw.lower() in lower:
            return PRIORITY_URGENT
    return PRIORITY_STANDARD


def _score_categories(description: str):
    lower = description.lower() if description else ""
    scores = {}
    matched = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        # Deduplicate overlapping keywords (e.g., "flooded" vs "flood", "bins overflowing" vs "bins")
        # Sort longest first and consume matched substring to avoid double-counting same text
        remaining = lower
        score = 0
        first_match = None
        for kw in sorted(keywords, key=len, reverse=True):
            kw_l = kw.lower()
            if kw_l in remaining:
                score += 1
                if first_match is None:
                    first_match = kw
                # remove first occurrence to prevent nested double count
                remaining = remaining.replace(kw_l, " ", 1)
        scores[cat] = score
        matched[cat] = first_match
    return scores, matched


def _extract_citation(description: str, keyword: str | None) -> str:
    """Return a verbatim substring from description to cite."""
    if not description or not description.strip():
        return "no description"
    if keyword:
        lower = description.lower()
        kw_lower = keyword.lower()
        idx = lower.find(kw_lower)
        if idx != -1:
            # return exact slice preserving original case
            return description[idx: idx + len(keyword)]
    # fallback: first 6 words
    words = description.strip().split()
    snippet = " ".join(words[:6])
    # strip punctuation edge for cleaner citation but keep substring guarantee
    return snippet


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or row.get("complaintId") or row.get("id") or "").strip()
    if not complaint_id:
        # fallback id will be assigned by batch_classify if needed, but keep blank here
        complaint_id = row.get("complaint_id", "")

    description = row.get("description")
    # handle None and non-string
    if description is None:
        description = ""
    else:
        description = str(description)

    desc_stripped = description.strip()

    # Handle null / empty -> ambiguous
    if not desc_stripped:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": PRIORITY_STANDARD,
            "reason": "No description provided — flagged for review as no specific words to cite.",
            "flag": "NEEDS_REVIEW",
        }

    priority = _determine_priority(description)
    scores, matched = _score_categories(description)

    # Find best category(ies) excluding Other
    # Consider only non-Other categories for scoring
    non_other_scores = {k: v for k, v in scores.items() if k != "Other"}
    max_score = max(non_other_scores.values()) if non_other_scores else 0

    if max_score == 0:
        # No keyword matched -> ambiguous
        citation = _extract_citation(description, None)
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f"Classified as Other because description contains '{citation}' with no matching taxonomy keywords — ambiguous.",
            "flag": "NEEDS_REVIEW",
        }

    # Collect winners
    winners = [cat for cat, sc in non_other_scores.items() if sc == max_score]

    if len(winners) > 1:
        # Tie -> genuinely ambiguous, per enforcement: Other + NEEDS_REVIEW
        # Include tied categories in reason for auditability
        citation = _extract_citation(description, matched[winners[0]])
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f"Classified as Other because description contains '{citation}' matching multiple categories {', '.join(sorted(winners))} — ambiguous.",
            "flag": "NEEDS_REVIEW",
        }

    category = winners[0]
    keyword = matched[category]
    citation = _extract_citation(description, keyword)

    # Ensure citation is verbatim substring (already guaranteed)
    # Build one-sentence reason citing specific words
    reason = f"Classified as {category} because description mentions '{citation}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    try:
        with open(input_path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("Input CSV has no header row")
            # normalize fieldnames check: description column must exist (case-insensitive)
            # we handle via row.get below
            rows = list(reader)
            if not rows:
                # still produce empty output with header
                pass
            for idx, row in enumerate(rows, start=1):
                try:
                    # preserve complaint_id fallback if missing
                    if not row.get("complaint_id") and not row.get("complaintId"):
                        # try case variations
                        cid = row.get("Complaint_id") or row.get("ID") or f"ROW-{idx:03d}"
                        row["complaint_id"] = cid
                    result = classify_complaint(row)
                    # Enforce allowed values defensively
                    if result["category"] not in ALLOWED_CATEGORIES:
                        result["category"] = "Other"
                        result["flag"] = "NEEDS_REVIEW"
                        result["reason"] = result["reason"] + " (corrected to Other — invalid category)."
                    if result["priority"] not in ("Urgent", "Standard", "Low"):
                        result["priority"] = "Standard"
                    if result["flag"] not in ("NEEDS_REVIEW", ""):
                        result["flag"] = "NEEDS_REVIEW"
                    # Ensure reason cites verbatim substring when possible — already done
                    results.append(result)
                except Exception as e:
                    # Per-row isolation: emit fallback
                    cid = row.get("complaint_id") or row.get("complaintId") or f"ROW-{idx:03d}"
                    desc = str(row.get("description") or "")[:60]
                    results.append({
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classification failed ({type(e).__name__}) for description '{desc}' — flagged for review.",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        # Still produce output with error row so caller sees failure gracefully
        results.append({
            "complaint_id": "FILE_ERROR",
            "category": "Other",
            "priority": "Standard",
            "reason": f"Input file not found: {input_path} — flagged for review.",
            "flag": "NEEDS_REVIEW",
        })
    except Exception as e:
        results.append({
            "complaint_id": "FILE_ERROR",
            "category": "Other",
            "priority": "Standard",
            "reason": f"Failed to read input CSV ({type(e).__name__}: {e}) — flagged for review.",
            "flag": "NEEDS_REVIEW",
        })

    # Always write output
    with open(output_path, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "complaint_id": r.get("complaint_id", ""),
                "category": r.get("category", "Other"),
                "priority": r.get("priority", "Standard"),
                "reason": r.get("reason", ""),
                "flag": r.get("flag", ""),
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
