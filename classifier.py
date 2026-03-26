"""
UC-0A: Civic Complaint Classifier
==================================
Reads a city test CSV (complaint_id, complaint_text),
classifies each complaint by category and severity,
and writes results_<city>.csv.

Usage:
    python classifier.py --input data/city-test-files/test_hyderabad.csv
    python classifier.py --input data/city-test-files/test_pune.csv
    python classifier.py --self-test

Author: AI Code Sarathi — UC-0A Submission
CRAFT Commit Trail:
  UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers
  UC-0A Fix category fallback: unknown text silently dropped → added OTHER + LOW default
  UC-0A Fix CSV encoding: non-UTF8 chars crashed reader → added errors='replace'
  UC-0A Fix self-test: no validation loop existed → added 8-case assertion suite
"""

import csv
import sys
import os
import argparse
import re

# ─────────────────────────────────────────────
# TAXONOMY
# ─────────────────────────────────────────────

CATEGORIES = [
    "ROAD_DAMAGE",
    "WATER_SUPPLY",
    "ELECTRICITY",
    "GARBAGE_COLLECTION",
    "SEWAGE_DRAINAGE",
    "STREET_LIGHTING",
    "PUBLIC_HEALTH",
    "NOISE_POLLUTION",
    "ENCROACHMENT",
    "PARKS_AND_RECREATION",
    "STRAY_ANIMALS",
    "OTHER",
]

SEVERITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

# ─────────────────────────────────────────────
# KEYWORD MAPS (category detection)
# ─────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    # ELECTRICITY checked FIRST so "wire near footpath" → ELECTRICITY not ROAD_DAMAGE
    "ELECTRICITY": [
        "live wire", "exposed wire", "hanging wire", "wire near",
        "electricity", "power cut", "power outage", "outage",
        "transformer", "electric meter", "electric",
        "voltage", "shock", "no power", "current",
    ],
    "ROAD_DAMAGE": [
        "pothole", "highway", "pavement",
        "crater", "road damage", "speed breaker", "road broken",
        "road collapse", "road caved", "tar road", "asphalt",
        "road cave", "road repair", "road condition",
    ],
    "WATER_SUPPLY": [
        "water", "supply", "tap", "pipeline", "no water",
        "water cut", "water shortage", "drinking water", "borewell",
        "water pipe", "tanker",
    ],
    "GARBAGE_COLLECTION": [
        "garbage", "waste", "trash", "rubbish", "dump",
        "litter", "bins", "collection", "solid waste",
        "garbage not collected", "overflowing bin",
    ],
    "SEWAGE_DRAINAGE": [
        "sewage", "drain", "drainage", "overflow", "blocked drain",
        "manhole", "sewer", "stormwater", "nala", "gutter",
    ],
    "STREET_LIGHTING": [
        "streetlight", "street light", "lamp post", "dark road",
        "lighting", "light not working", "no light", "street lamp",
    ],
    "PUBLIC_HEALTH": [
        "mosquito", "dengue", "malaria", "rat", "pest",
        "smell", "stench", "disease", "health", "hygiene",
        "contaminated", "dirty water", "dead animal smell",
    ],
    "NOISE_POLLUTION": [
        "noise", "loud", "music", "sound", "construction noise",
        "horn blaring", "speaker", "dj", "blaring", "disturbance",
    ],
    "ENCROACHMENT": [
        "encroachment", "illegal construction", "hawker",
        "footpath blocked", "property dispute", "illegal shop",
        "squatter", "occupied",
    ],
    "PARKS_AND_RECREATION": [
        "park", "garden", "playground", "tree fell", "bench",
        "grass", "recreation", "public garden", "walking track",
    ],
    "STRAY_ANIMALS": [
        "stray dog", "stray animal", "dog bite", "cattle",
        "cow", "dog", "animal", "stray", "horse",
    ],
}

# ─────────────────────────────────────────────
# SEVERITY KEYWORD TRIGGERS
# ─────────────────────────────────────────────

CRITICAL_TRIGGERS = [
    "injur", "accident", "collapse", "fire", "flood inside",
    "exposed live wire", "live wire", "exposed wire",
    "sewage overflow near hospital", "sewage overflow near school",
    # Fix: 'hospital' + 'sewage' combo → CRITICAL even without exact phrase
    "building collapse", "fallen tree blocking road",
    "blocked road completely", "electrocut", "dead body",
]

HIGH_TRIGGERS = [
    "child", "school", "no water for",
    "road cave", "dead animal on road", "garbage pile",
    "garbage not collected for", "broken streetlight on highway",
    "pothole on highway", "pothole on main road",
    "flooding", "flood", "sewage overflow",
    "fallen tree",
    # Note: 'hospital' moved below — handled in combo logic
]

MEDIUM_TRIGGERS = [
    "pothole", "intermittent", "flickering", "night",
    "stray dog", "not working",
    # Fix: removed "broken" from MEDIUM — too broad, caused park bench false positive
]

# ─────────────────────────────────────────────
# SKILL 1: classify_complaint
# ─────────────────────────────────────────────

def classify_complaint(complaint_text: str) -> dict:
    """
    Returns dict with keys: category, severity, reason
    CRAFT fix: severity blindness corrected — critical/high keywords enforced.
    """
    text_lower = complaint_text.lower()

    # ── Step 1: detect category ──
    detected_category = "OTHER"
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                detected_category = category
                break
        if detected_category != "OTHER":
            break

    # ── Step 2: detect severity ──
    severity = _detect_severity(text_lower)

    # ── Step 3: generate reason ──
    reason = _generate_reason(detected_category, severity, complaint_text)

    return {
        "category": detected_category,
        "severity": severity,
        "reason": reason,
    }


# ─────────────────────────────────────────────
# SKILL 2: detect_severity
# ─────────────────────────────────────────────

def _detect_severity(text_lower: str) -> str:
    """
    CRAFT fix 1: hard override rules for injury/child/school/hospital.
    CRAFT fix 2: sewage + hospital combo → CRITICAL (not just HIGH).
    CRAFT fix 3: removed 'broken' as MEDIUM trigger (too broad).
    """
    # ── Combo rules (evaluated before single-keyword rules) ──
    # Sewage near hospital or school → CRITICAL
    if ("sewage" in text_lower or "drain" in text_lower) and \
       ("hospital" in text_lower or "school" in text_lower):
        return "CRITICAL"

    # Check CRITICAL single-keyword triggers
    for trigger in CRITICAL_TRIGGERS:
        if trigger in text_lower:
            return "CRITICAL"

    # Hospital alone (not near sewage) → HIGH
    if "hospital" in text_lower:
        return "HIGH"

    # Check HIGH triggers
    for trigger in HIGH_TRIGGERS:
        if trigger in text_lower:
            return "HIGH"

    # Duration patterns → HIGH if ≥3 days
    duration_match = re.search(r'(\d+)\s*(day|days|week|weeks)', text_lower)
    if duration_match:
        n = int(duration_match.group(1))
        unit = duration_match.group(2)
        days = n * 7 if "week" in unit else n
        if days >= 3:
            return "HIGH"

    # Check MEDIUM
    for trigger in MEDIUM_TRIGGERS:
        if trigger in text_lower:
            return "MEDIUM"

    return "LOW"


def _generate_reason(category: str, severity: str, original_text: str) -> str:
    """Produces a short human-readable reason for the classification."""
    reasons = {
        ("ROAD_DAMAGE", "CRITICAL"): "Road damage caused injury or accident — immediate danger to life.",
        ("ROAD_DAMAGE", "HIGH"):     "Significant road damage on a major road posing safety risk.",
        ("ROAD_DAMAGE", "MEDIUM"):   "Pothole or road damage causing moderate inconvenience.",
        ("ROAD_DAMAGE", "LOW"):      "Minor road surface issue with low safety impact.",
        ("WATER_SUPPLY", "CRITICAL"): "Complete water failure near critical facility — urgent.",
        ("WATER_SUPPLY", "HIGH"):    "No water supply for 3+ days affecting many residents.",
        ("WATER_SUPPLY", "MEDIUM"):  "Intermittent water supply causing regular inconvenience.",
        ("WATER_SUPPLY", "LOW"):     "Minor water pressure issue with minimal impact.",
        ("ELECTRICITY", "CRITICAL"): "Exposed live wire or electrical hazard — immediate life risk.",
        ("ELECTRICITY", "HIGH"):     "Extended power outage affecting essential services.",
        ("ELECTRICITY", "MEDIUM"):   "Intermittent power cuts causing regular disruption.",
        ("ELECTRICITY", "LOW"):      "Minor electrical issue not posing safety risk.",
        ("GARBAGE_COLLECTION", "HIGH"):   "Garbage uncollected for several days — public health hazard.",
        ("GARBAGE_COLLECTION", "MEDIUM"): "Irregular garbage collection causing localised inconvenience.",
        ("GARBAGE_COLLECTION", "LOW"):    "Minor garbage issue with limited impact.",
        ("SEWAGE_DRAINAGE", "CRITICAL"):  "Sewage overflow near hospital or school — critical health risk.",
        ("SEWAGE_DRAINAGE", "HIGH"):      "Sewage overflow causing flooding or widespread contamination.",
        ("SEWAGE_DRAINAGE", "MEDIUM"):    "Blocked drain causing intermittent waterlogging.",
        ("SEWAGE_DRAINAGE", "LOW"):       "Minor drain blockage with limited impact.",
        ("STREET_LIGHTING", "HIGH"):   "Broken streetlight near school or highway — safety risk for pedestrians.",
        ("STREET_LIGHTING", "MEDIUM"): "Streetlight outage causing inconvenience but limited safety risk.",
        ("STREET_LIGHTING", "LOW"):    "Dim or intermittently working streetlight.",
        ("PUBLIC_HEALTH", "CRITICAL"): "Immediate public health hazard — disease vector or contamination risk.",
        ("PUBLIC_HEALTH", "HIGH"):     "Significant public health concern requiring prompt action.",
        ("PUBLIC_HEALTH", "MEDIUM"):   "Public health nuisance causing moderate concern.",
        ("PUBLIC_HEALTH", "LOW"):      "Minor cleanliness issue with low health impact.",
        ("NOISE_POLLUTION", "HIGH"):   "Excessive noise near hospital or school — affecting vulnerable groups.",
        ("NOISE_POLLUTION", "MEDIUM"): "Nighttime noise disturbance causing sleep disruption.",
        ("NOISE_POLLUTION", "LOW"):    "Daytime noise of limited duration or impact.",
        ("ENCROACHMENT", "HIGH"):      "Encroachment blocking emergency access or major thoroughfare.",
        ("ENCROACHMENT", "MEDIUM"):    "Encroachment causing moderate obstruction to public space.",
        ("ENCROACHMENT", "LOW"):       "Minor encroachment not blocking primary access.",
        ("PARKS_AND_RECREATION", "HIGH"):   "Safety hazard in park affecting children or elderly.",
        ("PARKS_AND_RECREATION", "MEDIUM"): "Park facility in disrepair causing inconvenience.",
        ("PARKS_AND_RECREATION", "LOW"):    "Minor cosmetic or maintenance issue in public park.",
        ("STRAY_ANIMALS", "CRITICAL"): "Stray animal bite or attack near school — immediate safety risk.",
        ("STRAY_ANIMALS", "HIGH"):     "Stray animals near school or hospital posing safety risk to children.",
        ("STRAY_ANIMALS", "MEDIUM"):   "Stray animal sighting causing public inconvenience.",
        ("STRAY_ANIMALS", "LOW"):      "Stray animal presence without immediate safety concern.",
        ("OTHER", "HIGH"):   "Complaint describes a serious issue not fitting standard categories.",
        ("OTHER", "MEDIUM"): "Complaint describes a moderate issue requiring attention.",
        ("OTHER", "LOW"):    "General complaint not fitting standard categories — low priority.",
    }
    key = (category, severity)
    return reasons.get(key, f"{category.replace('_',' ').title()} issue classified as {severity} priority.")


# ─────────────────────────────────────────────
# SKILL 3: CSV I/O
# ─────────────────────────────────────────────

def read_complaints_csv(filepath: str) -> list:
    """
    CRAFT fix: UTF-8 with errors='replace' prevents crash on non-ASCII input.
    """
    complaints = []
    with open(filepath, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # row 1 is header
            cid = row.get("complaint_id", "").strip()
            text = row.get("complaint_text", "").strip()
            if not text:
                print(f"[WARN] Row {i}: empty complaint_text — skipping.", file=sys.stderr)
                continue
            complaints.append({"complaint_id": cid, "complaint_text": text})
    return complaints


def write_results_csv(results: list, output_path: str):
    fieldnames = ["complaint_id", "complaint_text", "category", "severity", "reason"]
    with open(output_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"[OK] Results written to: {output_path}")


# ─────────────────────────────────────────────
# SKILL 4: Batch Processing
# ─────────────────────────────────────────────

def batch_classify(complaints: list) -> list:
    results = []
    errors = 0
    for row in complaints:
        try:
            result = classify_complaint(row["complaint_text"])
            results.append({
                "complaint_id":   row["complaint_id"],
                "complaint_text": row["complaint_text"],
                "category":       result["category"],
                "severity":       result["severity"],
                "reason":         result["reason"],
            })
        except Exception as e:
            errors += 1
            print(f"[ERROR] complaint_id={row.get('complaint_id','?')}: {e}", file=sys.stderr)
    print(f"[DONE] Processed: {len(results)} | Errors: {errors}")
    return results


# ─────────────────────────────────────────────
# SKILL 5: Self-Test (CRAFT Loop Validation)
# ─────────────────────────────────────────────

SELF_TEST_CASES = [
    {
        "text": "Large pothole on the highway caused a motorcycle accident, rider injured",
        "expected_category": "ROAD_DAMAGE",
        "expected_severity": "CRITICAL",
    },
    {
        "text": "No water supply for 4 days in our colony, please fix immediately",
        "expected_category": "WATER_SUPPLY",
        "expected_severity": "HIGH",
    },
    {
        "text": "Stray dogs near school gate, children are afraid to walk",
        "expected_category": "STRAY_ANIMALS",
        "expected_severity": "HIGH",
    },
    {
        "text": "Park bench near the entrance is broken and needs repair",
        "expected_category": "PARKS_AND_RECREATION",
        "expected_severity": "LOW",
    },
    {
        "text": "Exposed live wire hanging near the footpath after last night storm",
        "expected_category": "ELECTRICITY",
        "expected_severity": "CRITICAL",
    },
    {
        "text": "Garbage not collected for 6 days, unbearable smell on the street",
        "expected_category": "GARBAGE_COLLECTION",
        "expected_severity": "HIGH",
    },
    {
        "text": "Loud music from nearby bar after midnight, unable to sleep",
        "expected_category": "NOISE_POLLUTION",
        "expected_severity": "MEDIUM",
    },
    {
        "text": "Sewage overflowing right outside the government hospital entrance",
        "expected_category": "SEWAGE_DRAINAGE",
        "expected_severity": "CRITICAL",
    },
]


def run_self_test():
    print("\n" + "="*60)
    print("SELF-TEST — UC-0A Complaint Classifier")
    print("="*60)
    passed = 0
    failed = 0
    for i, tc in enumerate(SELF_TEST_CASES, 1):
        result = classify_complaint(tc["text"])
        cat_ok = result["category"] == tc["expected_category"]
        sev_ok = result["severity"] == tc["expected_severity"]
        status = "✅ PASS" if (cat_ok and sev_ok) else "❌ FAIL"
        if cat_ok and sev_ok:
            passed += 1
        else:
            failed += 1
        print(f"\nTest {i}: {status}")
        print(f"  Text    : {tc['text'][:70]}...")
        print(f"  Category: got={result['category']:25s} expected={tc['expected_category']}")
        print(f"  Severity: got={result['severity']:10s} expected={tc['expected_severity']}")
        if not cat_ok or not sev_ok:
            print(f"  Reason  : {result['reason']}")

    print("\n" + "="*60)
    print(f"RESULT: {passed}/{len(SELF_TEST_CASES)} passed, {failed} failed")
    print("="*60 + "\n")
    return failed == 0


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0A Civic Complaint Classifier"
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to input CSV (e.g. data/city-test-files/test_hyderabad.csv)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path for output CSV (default: results_<city>.csv in same folder)"
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="Run built-in self-test suite and exit"
    )
    args = parser.parse_args()

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    if not args.input:
        print("[ERROR] Please provide --input <csv_path> or use --self-test")
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}")
        sys.exit(1)

    # Derive output path
    if args.output:
        output_path = args.output
    else:
        base = os.path.basename(args.input)           # test_hyderabad.csv
        city = base.replace("test_", "").replace(".csv", "")  # hyderabad
        out_dir = os.path.dirname(args.input)
        output_path = os.path.join(out_dir, f"results_{city}.csv")

    print(f"[INFO] Reading: {args.input}")
    complaints = read_complaints_csv(args.input)
    print(f"[INFO] Complaints loaded: {len(complaints)}")

    results = batch_classify(complaints)
    write_results_csv(results, output_path)


if __name__ == "__main__":
    main()
