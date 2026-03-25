"""
UC-0A — Complaint Classifier  (Logistic Regression edition)
Implements classify_complaint and batch_classify as defined in agents.md and skills.md.

The Anthropic API has been replaced by a TF-IDF + Logistic Regression model trained on
hand-crafted labelled examples that cover all 10 allowed categories.

Enforcement rules from agents.md are applied as hardcoded Python checks AFTER
the model predicts — the model output is never trusted unconditionally.
"""
import argparse
import csv
import json
import os
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# ---------------------------------------------------------------------------
# Constants — must match agents.md exactly
# ---------------------------------------------------------------------------

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

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

# agents.md: keywords that must trigger Urgent priority
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
}

# skills.md: candidate column names for the description field
DESCRIPTION_COLUMN_CANDIDATES = [
    "description", "complaint_description", "text", "details",
]

# Fallback returned on any error or parse failure
FALLBACK = {
    "category": "Other",
    "priority": "Standard",
    "reason": "Classification failed due to error.",
    "flag": "NEEDS_REVIEW",
}

# ---------------------------------------------------------------------------
# Training data — labelled examples for all 10 categories
# ---------------------------------------------------------------------------

TRAINING_DATA = [
    # Pothole
    ("Large pothole on the road causing tyre damage to vehicles", "Pothole"),
    ("Deep crater-sized pothole near the bus stop", "Pothole"),
    ("Pothole 60 cm wide on main road, three vehicles affected", "Pothole"),
    ("Road has multiple potholes after rain, driving is dangerous", "Pothole"),
    ("Pothole near traffic signal causing accidents", "Pothole"),
    ("Big pothole at the intersection, cars swerving to avoid it", "Pothole"),
    ("Several potholes on the highway stretch making it unsafe", "Pothole"),

    # Flooding
    ("Underpass flooded knee-deep after two hours of rain", "Flooding"),
    ("Flood water entered homes in the low-lying area", "Flooding"),
    ("Street flooded after heavy rainfall, commuters stranded", "Flooding"),
    ("Bridge approach floods within 30 minutes of rain", "Flooding"),
    ("Water logging on main road causing traffic jam", "Flooding"),
    ("Colony roads flooded, vehicles submerged", "Flooding"),
    ("Market area waterlogged after monsoon showers", "Flooding"),

    # Streetlight
    ("Three consecutive streetlights out for 10 days, area very dark", "Streetlight"),
    ("Streetlight flickering and not working near the park", "Streetlight"),
    ("No street lights on the entire stretch of road for a week", "Streetlight"),
    ("Street lamp broken at the junction, pedestrians at risk", "Streetlight"),
    ("Lights not working in the residential area since two weeks", "Streetlight"),
    ("Overhead street light pole fallen on footpath", "Streetlight"),
    ("Two streetlights damaged, area pitch dark at night", "Streetlight"),

    # Waste
    ("Overflowing garbage bins near vegetable market, unbearable smell", "Waste"),
    ("Garbage not collected for five days, piling up on the road", "Waste"),
    ("Bulk waste from apartment renovation dumped on public road", "Waste"),
    ("Waste dump near residential area attracting stray animals", "Waste"),
    ("Dead animal not removed for 36 hours, health concern", "Waste"),
    ("Illegal garbage dumping on the footpath by residents", "Waste"),
    ("Solid waste piled on open ground for two weeks", "Waste"),

    # Noise
    ("Wedding venue playing loud music past midnight on weeknights", "Noise"),
    ("Construction site noise at 2 am, residents cannot sleep", "Noise"),
    ("Loud music from club disturbing residents every night", "Noise"),
    ("Factory generating excessive noise during prohibited hours", "Noise"),
    ("DJ party noise pollution past 11 pm near school area", "Noise"),
    ("Persistent honking from vehicles near residential zone", "Noise"),
    ("Loud generator running at night disturbing neighbourhood", "Noise"),

    # Road Damage
    ("Road surface cracked and sinking near utility work", "Road Damage"),
    ("Footpath tiles broken and upturned, dangerous for pedestrians", "Road Damage"),
    ("Manhole cover missing on the road, risk of injury to cyclists", "Road Damage"),
    ("Asphalt peeling off on the highway after monsoon", "Road Damage"),
    ("Road shoulders eroded after heavy rain", "Road Damage"),
    ("Divider damaged on the main road due to accident", "Road Damage"),
    ("Service road broken and uneven near the flyover", "Road Damage"),

    # Heritage Damage
    ("Heritage wall defaced with graffiti near old city area", "Heritage Damage"),
    ("Vandalism reported at the heritage monument", "Heritage Damage"),
    ("Historical building facade damaged due to neglect", "Heritage Damage"),
    ("Heritage street lights out, safety concern for pedestrians after dark", "Heritage Damage"),
    ("Old fort wall crumbling, preservation needed urgently", "Heritage Damage"),
    ("Ancient step well damaged by construction activity nearby", "Heritage Damage"),
    ("Heritage site encroached upon by vendors", "Heritage Damage"),

    # Heat Hazard
    ("No shade or drinking water at bus stop during extreme heat", "Heat Hazard"),
    ("Heat wave causing illness among elderly residents", "Heat Hazard"),
    ("Open tar road radiating excessive heat in summer", "Heat Hazard"),
    ("No trees on walking path, unbearable heat for commuters", "Heat Hazard"),
    ("Residents suffering from heat exhaustion due to power cuts", "Heat Hazard"),
    ("High temperature alert, no cool shelter available near market", "Heat Hazard"),
    ("Metal bus shelter overheating in summer, burning commuters", "Heat Hazard"),

    # Drain Blockage
    ("Bus stand flooded because drain is completely blocked", "Drain Blockage"),
    ("Drain clogged with debris causing water to overflow onto road", "Drain Blockage"),
    ("Storm drain blocked by plastic waste, flooding nearby houses", "Drain Blockage"),
    ("Main drain blocked for two weeks, foul smell in the area", "Drain Blockage"),
    ("Sewage drain blocked causing overflow on footpath", "Drain Blockage"),
    ("Gutter choked and overflowing into the residential lane", "Drain Blockage"),
    ("Blocked drain leading to mosquito breeding near water body", "Drain Blockage"),

    # Other
    ("Stray dogs aggressive near park posing danger to residents", "Other"),
    ("Encroachment on public footpath by shop owners", "Other"),
    ("Unauthorised construction blocking natural light to adjacent building", "Other"),
    ("Complaint about neighbour dispute, mediation requested", "Other"),
    ("Issue with water supply in the morning hours", "Other"),
    ("Electricity meter faulty, readings incorrect", "Other"),
    ("Tree fell on car in storm, insurance query", "Other"),
]

# ---------------------------------------------------------------------------
# Build and train the classifier pipeline at import time
# ---------------------------------------------------------------------------

_TRAIN_TEXTS  = [text for text, _ in TRAINING_DATA]
_TRAIN_LABELS = [label for _, label in TRAINING_DATA]

_MODEL: Pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )),
    ("lr", LogisticRegression(
        max_iter=1000,
        C=5.0,
        class_weight="balanced",
        solver="lbfgs",
    )),
])
_MODEL.fit(_TRAIN_TEXTS, _TRAIN_LABELS)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _detect_description_column(fieldnames: list) -> str:
    """
    Return the actual fieldname matching a known description column (case-insensitive).
    Raises KeyError if none of the candidates are present.
    """
    lower_map = {f.lower(): f for f in fieldnames}
    for candidate in DESCRIPTION_COLUMN_CANDIDATES:
        if candidate in lower_map:
            return lower_map[candidate]
    raise KeyError(
        f"No description column found. Candidates: {DESCRIPTION_COLUMN_CANDIDATES}. "
        f"Available columns: {fieldnames}"
    )


def _predict_with_confidence(description: str) -> tuple[str, float]:
    """
    Run the LR pipeline on a description string.
    Returns (predicted_category, max_probability).
    """
    proba = _MODEL.predict_proba([description])[0]
    classes = _MODEL.classes_
    idx = int(np.argmax(proba))
    return classes[idx], float(proba[idx])


def _derive_priority(description: str) -> str:
    """
    Determine priority from description:
    - Urgent if any severity keyword present (agents.md rule)
    - Standard otherwise (Low is reserved for model-suggested minor issues)
    """
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, confidence: float) -> str:
    """
    Generate a one-sentence reason citing words from the description, as required
    by agents.md: 'reason — one sentence citing specific words from the complaint description'.
    """
    # Find the most relevant phrase (first 12 words of description)
    words = description.split()
    excerpt = " ".join(words[:12])
    if len(words) > 12:
        excerpt += "..."
    return (
        f"Classified as '{category}' based on description: \"{excerpt}\" "
        f"(model confidence {confidence:.0%})."
    )


def _enforce(result: dict, description: str) -> dict:
    """
    Post-call enforcement layer — applies every agents.md rule in Python.
    Called after the model predicts; the model is never trusted unconditionally.
    """
    # Rule 1 — category must exactly match the allowed set
    if result.get("category") not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"

    # Rule 2 — severity keyword in description → force Urgent (case-insensitive)
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in SEVERITY_KEYWORDS):
        result["priority"] = "Urgent"

    # Rule 3 — priority must be a legal value
    if result.get("priority") not in ALLOWED_PRIORITIES:
        result["priority"] = "Standard"

    # Rule 4 — reason must be a non-empty string
    if not isinstance(result.get("reason"), str) or not result["reason"].strip():
        result["reason"] = "No reason provided by model."

    # Rule 5 — flag must be "NEEDS_REVIEW" or ""
    if result.get("flag") not in ("NEEDS_REVIEW", "", None):
        result["flag"] = "NEEDS_REVIEW"
    if result.get("flag") is None:
        result["flag"] = ""

    return result


# ---------------------------------------------------------------------------
# Skill 1 — classify_complaint  (agents.md → intent + enforcement)
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using the TF-IDF + Logistic Regression model.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Applies every enforcement rule from agents.md as hardcoded Python checks
    AFTER the model predicts — never trusts model output unconditionally.
    On any error returns the FALLBACK record and never raises.
    """
    # Resolve the description column from whatever keys the row provides
    try:
        desc_col = _detect_description_column(list(row.keys()))
        description = str(row.get(desc_col, "")).strip()
    except KeyError:
        description = ""

    complaint_id = row.get("complaint_id", "")

    try:
        category, confidence = _predict_with_confidence(description)

        # Low-confidence predictions are flagged for review
        flag = "NEEDS_REVIEW" if confidence < 0.30 else ""

        priority = _derive_priority(description)
        reason   = _build_reason(description, category, confidence)

        result = {
            "category": category,
            "priority": priority,
            "reason":   reason,
            "flag":     flag,
        }

    except Exception as exc:
        print(f"  [ERROR] classify_complaint failed for complaint_id={complaint_id!r}: {exc}")
        result = dict(FALLBACK)

    # Mandatory post-call enforcement — agents.md rules applied in Python
    result = _enforce(result, description)

    return {
        "complaint_id": complaint_id,
        "category":     result["category"],
        "priority":     result["priority"],
        "reason":       result["reason"],
        "flag":         result["flag"],
    }


# ---------------------------------------------------------------------------
# Skill 2 — batch_classify  (skills.md → batch_classify definition)
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read an input CSV of complaint rows, apply classify_complaint to each row,
    and write a classified output CSV with all original columns plus:
    category, priority, reason, flag.

    - Raises FileNotFoundError if input_path is missing or unreadable.
    - Never crashes on a bad individual row — writes the fallback record instead.
    - Prints progress per row: "Classifying row N/Total: [complaint_id]"
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        input_rows = list(reader)
        original_fieldnames = list(reader.fieldnames or [])

    # Output columns = all original + classification cols (deduped, order preserved)
    classification_cols = ["category", "priority", "reason", "flag"]
    extra_cols = [c for c in classification_cols if c not in original_fieldnames]
    output_fieldnames = original_fieldnames + extra_cols

    results = []
    total = len(input_rows)

    for i, row in enumerate(input_rows, start=1):
        cid = row.get("complaint_id", str(i))
        print(f"Classifying row {i}/{total}: {cid}")

        try:
            classified = classify_complaint(row)
        except Exception as exc:
            print(f"  [ERROR] Unexpected failure on row {i} (complaint_id={cid!r}): {exc}")
            classified = {"complaint_id": cid, **FALLBACK}

        # Merge classification fields back into a copy of the original row
        out_row = dict(row)
        for col in classification_cols:
            out_row[col] = classified.get(col, FALLBACK.get(col, ""))

        results.append(out_row)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Classified {total} rows → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier (Logistic Regression)")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
