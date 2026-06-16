"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
from pathlib import Path
from typing import Optional

# Optional ML imports handled at runtime
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import make_pipeline
    _SKLEARN_AVAILABLE = True
except Exception:
    _SKLEARN_AVAILABLE = False
# joblib for model persistence
try:
    from joblib import dump as _joblib_dump, load as _joblib_load
    _JOBLIB_AVAILABLE = True
except Exception:
    try:
        # older sklearn bundle
        from sklearn.externals.joblib import dump as _joblib_dump, load as _joblib_load
        _JOBLIB_AVAILABLE = True
    except Exception:
        _JOBLIB_AVAILABLE = False

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    # Basic defensive checks
    if not isinstance(row, dict):
        return {"complaint_id": None, "category": "Unknown", "priority": "low", "reason": "invalid row format", "flag": "error"}

    cid = row.get("complaint_id") or row.get("id") or None
    desc = (row.get("description") or "").strip()
    loc = (row.get("location") or "").strip()
    days_open_raw = row.get("days_open") or row.get("days") or ""

    flags = []
    missing = []
    if not cid:
        missing.append("complaint_id")
    if not desc:
        missing.append("description")
    if missing:
        flags.append("nulls")

    # normalize text for keyword matching
    text = f"{desc} {loc}".lower()

    # Load keyword configuration (module-level variable may be set)
    kw = globals().get("_KEYWORDS_CONFIG")
    if not kw:
        kw = {
            "categories": {
                "Pothole / Road": ["pothole", "potholes", "road surface", "sink", "crack", "sinking"],
                "Flooding": ["flood", "flooded", "underpass flooded", "knee-deep", "bridge approach floods", "water"],
                "Streetlight / Electrical": ["streetlight", "light out", "lights out", "flicker", "sparking", "electrical hazard", "street light"],
                "Garbage / Waste": ["garbage", "overflowing", "bins", "bulk waste", "waste", "dumped", "bin"],
                "Noise": ["music past", "noise", "loud music", "wedding venue", "music"],
                "Manhole / Safety": ["manhole", "missing cover", "man hole", "man-hole", "open manhole"],
                "Public Health": ["dead animal", "animal not removed", "dead animal not removed"],
            },
            "high_priority_keywords": ["risk", "injury", "missing", "knee-deep", "sparking", "electrical hazard", "school", "children", "manhole", "collision", "fatal", "open manhole"],
            "medium_priority_keywords": ["flood", "blocked", "overflow", "garbage", "pothole", "dead animal", "broken", "cracked", "overflowing"],
        }

    # If a keywords.json file lives in this package, load and merge it (allows local tuning)
    try:
        pkg_dir = Path(__file__).resolve().parent
        config_path = pkg_dir / "keywords.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as cf:
                file_kw = json.load(cf)
                # shallow merge: file overrides defaults
                kw.update(file_kw)
    except Exception:
        # ignore config load errors and continue with defaults
        pass

    # Category heuristics using keyword config
    category = "Other"
    cat_reasons = []
    for cat, keywords in kw.get("categories", {}).items():
        if any(k in text for k in keywords):
            category = cat
            cat_reasons.append(cat.lower())
            break

    # Priority heuristics
    priority = "low"
    try:
        days_open = int(days_open_raw) if str(days_open_raw).strip() else 0
    except Exception:
        days_open = 0

    high_keywords = kw.get("high_priority_keywords", [])
    med_keywords = kw.get("medium_priority_keywords", [])

    if any(k in text for k in high_keywords) or (category == "Manhole / Safety") or days_open >= 14:
        priority = "high"
    elif any(k in text for k in med_keywords) or (7 <= days_open < 14):
        priority = "medium"

    # Reason summarises matched cues
    reason_parts = []
    if cat_reasons:
        reason_parts.extend(cat_reasons)
    if days_open:
        reason_parts.append(f"days_open={days_open}")
    if not reason_parts:
        reason_parts.append("no specific keyword match")

    flag = ";".join(flags) if flags else "none"

    return {"complaint_id": cid, "category": category, "priority": priority, "reason": ", ".join(reason_parts), "flag": flag}


def _build_training_corpus(kw_config: dict, samples_per_keyword: int = 3):
    texts = []
    labels = []
    for cat, keywords in kw_config.get("categories", {}).items():
        for kw in keywords:
            for i in range(samples_per_keyword):
                texts.append(f"{kw} reported near main road")
                labels.append(cat)
                texts.append(f"{kw} causing issues for residents")
                labels.append(cat)
    return texts, labels


def enable_ml(train_from_keywords: bool = True) -> bool:
    """Attempt to enable an ML classifier.

    Returns True if an ML pipeline was successfully created and enabled, False otherwise.
    """
    global _SKLEARN_AVAILABLE
    if not _SKLEARN_AVAILABLE:
        return False

    # prepare keyword configuration (reuse existing loading logic)
    kw = globals().get("_KEYWORDS_CONFIG") or {}
    try:
        pkg_dir = Path(__file__).resolve().parent
        config_path = pkg_dir / "keywords.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as cf:
                file_kw = json.load(cf)
                kw.update(file_kw)
    except Exception:
        pass

    # build training data from keywords
    if train_from_keywords:
        texts, labels = _build_training_corpus(kw)
    else:
        texts, labels = [], []

    if not texts:
        return False

    try:
        vect = TfidfVectorizer()
        clf = MultinomialNB()
        pipeline = make_pipeline(vect, clf)
        pipeline.fit(texts, labels)
        globals()['_ML_PIPELINE'] = pipeline
        globals()['_USE_ML'] = True
        return True
    except Exception:
        return False


def save_model(path: str) -> bool:
    """Persist the trained ML pipeline to `path` using joblib."""
    if not _JOBLIB_AVAILABLE:
        return False
    pipeline = globals().get('_ML_PIPELINE')
    if pipeline is None:
        return False
    try:
        _joblib_dump(pipeline, path)
        return True
    except Exception:
        return False


def load_model(path: str) -> bool:
    """Load a persisted ML pipeline from `path` into the module globals."""
    if not _JOBLIB_AVAILABLE:
        return False
    try:
        pipeline = _joblib_load(path)
        globals()['_ML_PIPELINE'] = pipeline
        globals()['_USE_ML'] = True
        return True
    except Exception:
        return False



def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    # Read input CSV rows defensively, classify each and write results.
    with open(input_path, newline="", encoding="utf-8") as inf, open(output_path, "w", newline="", encoding="utf-8") as outf:
        reader = csv.DictReader(inf)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outf, fieldnames=fieldnames)
        writer.writeheader()

        row_index = 0
        for row in reader:
            row_index += 1
            try:
                result = classify_complaint(row)
                # Ensure result has all fields
                out_row = {k: result.get(k, None) for k in fieldnames}
            except Exception as e:
                # Don't crash — write an error row with minimal info
                cid = row.get("complaint_id") or f"ERROR_ROW_{row_index}"
                out_row = {"complaint_id": cid, "category": "Unknown", "priority": "low", "reason": f"classification_error: {str(e)}", "flag": "error"}

            writer.writerow(out_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — lightweight keyword-based classifier",
        epilog="Example: python uc-0a/classifier.py --input data/city-test-files/test_pune.csv --output results.csv",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV (e.g. test_pune.csv). Must contain complaint_id and description columns.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV. Will be overwritten if it exists.",
    )
    parser.add_argument("--version", action="version", version="uc-0a classifier 0.1")
    parser.add_argument("--use-ml", action="store_true", help="Enable ML-based classification if sklearn is available (trained from keywords.json).")
    args = parser.parse_args()
    if args.use_ml:
        ok = enable_ml()
        if not ok:
            print("ML pipeline not available or failed to train — falling back to keyword rules.")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
