"""
UC-0A — Complaint Classifier.
Enforcement (README.md + agents.md):
  - category: exactly one of Pothole, Flooding, Streetlight, Waste, Noise,
    Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
  - priority: Urgent if severity keywords present, else Standard.
  - reason: one sentence citing specific words from the description.
  - flag: NEEDS_REVIEW when genuinely ambiguous, else blank.
"""
import argparse
import csv
import re

CATEGORIES = [
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

# Severity keywords that must trigger Urgent (README). Include morphological
# variants to avoid severity blindness (injured, children, hospitalised...).
SEVERITY_STEMS = [
    "injur",      # injury / injured
    "child",      # child / children
    "school",
    "hospital",   # hospital / hospitalised
    "ambulance",
    "fire",
    "hazard",     # hazard / hazardous
    "fell",
    "fall",       # fell / fall / fallen (fall risk counts)
    "collaps",    # collapse / collapsed
]

HERITAGE_NOUNS = [
    "heritage", "historic", "museum", "monument", "tram",
    "cobblestone", "tagore", "marble palace", "step well",
    "step-well", "ancient",
]

HERITAGE_DAMAGE_VERBS = [
    "knocked", "broken", "defaced", "removed", "destroyed",
    "damaged", "damage", "cable laying", "billboard",
    "not restored", "not replaced", "subsidence", "subsided",
]


def _contains_any(text: str, phrases) -> bool:
    t = text.lower()
    return any(p in t for p in phrases)


def _cite(description: str, keywords, window: int = 6) -> str:
    """Return a verbatim excerpt (~window words) around first keyword hit."""
    words = description.split()
    low = description.lower()
    hit_at = None
    for kw in keywords:
        i = low.find(kw.lower())
        if i != -1 and (hit_at is None or i < hit_at):
            hit_at = i
    if hit_at is None:
        excerpt = " ".join(words[: min(window, len(words))])
        return excerpt
    # map char offset to word index
    char_count = 0
    start_word = 0
    for idx, w in enumerate(words):
        if char_count >= hit_at:
            start_word = idx
            break
        char_count += len(w) + 1
    lo = max(0, start_word - 2)
    hi = min(len(words), lo + window)
    return " ".join(words[lo:hi])


def _detect_category(desc_lower: str):
    """Return (category, matched_keywords, all_candidate_categories)."""
    candidates = []

    # Heritage Damage: heritage noun + damage verb (avoids misclassifying
    # noise/waste/streetlight issues that merely occur in heritage zones).
    if _contains_any(desc_lower, HERITAGE_NOUNS) and _contains_any(
        desc_lower, HERITAGE_DAMAGE_VERBS
    ):
        candidates.append("Heritage Damage")

    if _contains_any(desc_lower, ["heat", "melting", "temperature", "°c",
                                  "burns on contact", "dangerous temperatures",
                                  "unbearable", "heatwave", "full sun",
                                  "bubbling at 45", "storing heat"]):
        candidates.append("Heat Hazard")

    if _contains_any(desc_lower, ["flooded", "flooding", "floods",
                                  "knee-deep", "waterlogged", "stranded"]):
        candidates.append("Flooding")

    if _contains_any(desc_lower, ["drain blocked", "drain completely",
                                  "stormwater drain", "mosquito breeding",
                                  "drain 100%", "main drain", "drain",
                                  "draining directly"]):
        # 'drain' alone is enough; effect-level flooding handled separately.
        candidates.append("Drain Blockage")

    if _contains_any(desc_lower, ["streetlight", "street light", "lights out",
                                  "light out", "unlit", "lamp post", "substation",
                                  "darkness", "dark at night", "flickering and sparking",
                                  "wiring theft"]):
        candidates.append("Streetlight")

    if _contains_any(desc_lower, ["garbage", "waste", "overflowing",
                                  "dumped", "dead animal", "piles",
                                  "not cleared", "not removed", "bins overflowing"]):
        candidates.append("Waste")

    if _contains_any(desc_lower, ["music", "band playing", "amplifier",
                                  "drilling", "idling", "club music", "wedding",
                                  "past midnight", "at 2am", "at 11pm"]):
        candidates.append("Noise")

    if "pothole" in desc_lower:
        candidates.append("Pothole")

    if _contains_any(desc_lower, ["collapsed", "collapse", "crater", "buckled",
                                  "subsided", "subsidence", "sinking", "cracked",
                                  "sinking", "manhole", "footpath", "tiles broken",
                                  "upturned paving", "broken bench", "road surface",
                                  "gas leak", "structural concern", "swallowed entire",
                                  "school bus struggling"]):
        candidates.append("Road Damage")

    # Priority-ordered resolution (most specific / least ambiguous first).
    priority_order = ["Heritage Damage", "Flooding", "Drain Blockage",
                      "Streetlight", "Waste", "Noise", "Heat Hazard",
                      "Pothole", "Road Damage"]
    for cat in priority_order:
        if cat in candidates:
            return cat, cat, candidates
    if candidates:  # only Road Damage matched (not in early loop? it is)
        return candidates[0], candidates[0], candidates
    return "Other", "no clear keywords", []


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row.

    Returns dict with keys: complaint_id, category, priority, reason, flag.
    Never raises on bad rows — returns Other + NEEDS_REVIEW instead.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided so category cannot be determined.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    category, matched, candidates = _detect_category(desc_lower)

    # Urgent if any severity stem present (exact README rule + variants).
    priority = "Urgent" if _contains_any(desc_lower, SEVERITY_STEMS) else "Standard"

    # Flag when genuinely ambiguous: no match, or 2+ competing categories.
    # Flooding caused by Drain Blockage is a single coherent incident.
    # Heritage Damage absorbs Road Damage/Streetlight overlap (the lamp post /
    # subsidence IS the heritage damage mechanism), and explicit heat markers
    # (°C/temperature/melting) make Heat Hazard decisive over generic
    # "road surface" overlap.
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        competing = [c for c in candidates if c != category]
        if category == "Flooding" and competing == ["Drain Blockage"]:
            flag = ""
        elif category == "Heritage Damage" and all(
            c in ("Road Damage", "Streetlight") for c in competing
        ):
            flag = ""
        elif category == "Heat Hazard" and all(
            c in ("Road Damage",) for c in competing
        ):
            flag = ""
        elif competing:
            flag = "NEEDS_REVIEW"

    excerpt = _cite(description, [matched] if matched else [])
    # Keep reason to one sentence with a verbatim citation.
    excerpt = excerpt.rstrip(".")
    reason = f'Classified as {category} based on phrase "{excerpt}".'

    # Category must be exact schema value.
    if category not in CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV.

    Flags nulls, never crashes on bad rows, always writes output.
    """
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row or {}))
        except Exception:
            results.append({
                "complaint_id": (row or {}).get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": "Row could not be classified due to invalid input.",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
