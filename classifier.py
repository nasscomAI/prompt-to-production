"""
UC-0A: Complaint Classifier
============================
Classifies civic complaints from a CSV file into:
  - category   : Type of civic issue
  - severity   : Critical / High / Medium / Low
  - department : Responsible municipal department

Usage:
    python classifier.py --city pune
    python classifier.py --city hyderabad
    python classifier.py --city kolkata
    python classifier.py --city ahmedabad

Input  : data/city-test-files/test_[city].csv
Output : uc-0a/results_[city].csv

CRAFT Loop:
    Context  - Municipal civic grievance redressal
    Role     - Complaint triage classifier
    Action   - Classify each row: category + severity + department
    Format   - CSV output with audit log
    Tone     - Precise, consistent, rule-based
"""

import csv
import os
import sys
import argparse
import re
from datetime import datetime

# ---------------------------------------------------------------------------
# SKILL 1: Category Detection
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Roads": [
        "road", "pothole", "footpath", "bridge", "divider", "pavement",
        "speed breaker", "accident", "crater", "tar", "asphalt", "highway",
        "lane", "flyover", "underpass", "signal", "traffic"
    ],
    "Water": [
        "water", "pipe", "drainage", "sewage", "leakage", "leak", "flood",
        "supply", "borewell", "tank", "overflow", "sewer", "drain",
        "contamination", "dirty water", "no water"
    ],
    "Electricity": [
        "power", "electricity", "light", "streetlight", "transformer",
        "outage", "wire", "shock", "electrocution", "voltage", "cable",
        "blackout", "no electricity", "sparking", "tripping"
    ],
    "Sanitation": [
        "garbage", "waste", "trash", "dustbin", "sweeper", "smell",
        "dumping", "cleanliness", "litter", "rubbish", "sewage smell",
        "open defecation", "stray", "rat", "mosquito", "insects"
    ],
    "Safety": [
        "fire", "explosion", "danger", "threat", "harassment", "crime",
        "theft", "violence", "robbery", "assault", "unsafe", "attack",
        "burning", "smoke", "flames", "collapsed", "collapse"
    ],
    "Health": [
        "hospital", "clinic", "medicine", "disease", "epidemic", "ambulance",
        "dengue", "malaria", "fever", "infection", "health", "doctor",
        "patient", "medical", "ward", "quarantine"
    ],
    "Parks & Public Spaces": [
        "park", "garden", "playground", "bench", "tree", "encroachment",
        "open space", "footpath", "public toilet", "statue"
    ],
}

def detect_category(text: str) -> str:
    """
    Skill 1 — detect_category
    Scans complaint text for domain keywords and returns the best-matching category.
    """
    text_lower = text.lower()
    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score

    if not scores:
        return "General"

    # Return the category with the highest keyword match count
    return max(scores, key=scores.get)


# ---------------------------------------------------------------------------
# SKILL 2: Severity Classification
# ---------------------------------------------------------------------------

CRITICAL_TRIGGERS = [
    "injur", "injured", "dead", "death", "casualt", "fatal",
    "fire", "flood", "flooded", "flooding",
    "hospital", "clinic", "health centre",
    "child", "children", "school", "kindergarten",
    "emergency", "electrocution", "electrocuted",
    "explosion", "collapse", "collapsed", "building fell",
    "burning", "flames", "smoke", "accident"
]

HIGH_TRIGGERS = [
    "contamination", "contaminated", "no water", "water cut",
    "power cut", "no electricity", "blackout", "outage",
    "dangerous", "overflowing", "overflow", "blocked road",
    "road blocked", "major pothole", "deep pothole",
    "sparking wire", "live wire", "open manhole",
    "sewage overflow"
]

MEDIUM_TRIGGERS = [
    "pothole", "broken", "irregular", "intermittent",
    "dim light", "delayed", "leaking", "leak",
    "dirty", "clogged", "blocked drain", "stench", "smell",
    "garbage not collected", "no garbage"
]

def classify_severity(text: str) -> str:
    """
    Skill 2 — classify_severity
    Checks triggers in priority order: Critical → High → Medium → Low
    """
    text_lower = text.lower()

    # Critical check first — never override downward
    for trigger in CRITICAL_TRIGGERS:
        if trigger in text_lower:
            return "Critical"

    for trigger in HIGH_TRIGGERS:
        if trigger in text_lower:
            return "High"

    for trigger in MEDIUM_TRIGGERS:
        if trigger in text_lower:
            return "Medium"

    return "Low"


# ---------------------------------------------------------------------------
# SKILL 3: Department Routing
# ---------------------------------------------------------------------------

DEPARTMENT_MAP = {
    "Roads":               "PWD (Public Works Department)",
    "Water":               "Water Board",
    "Electricity":         "BESCOM / Electricity Board",
    "Sanitation":          "BBMP / Municipal Corporation",
    "Safety":              "Fire & Emergency Services / Police",
    "Health":              "Health Department",
    "Parks & Public Spaces": "BBMP / Municipal Corporation",
    "General":             "Municipal Corporation (General) — Manual Review Required",
}

def route_department(category: str) -> str:
    """
    Skill 3 — route_department
    Maps category to the responsible municipal department.
    """
    return DEPARTMENT_MAP.get(category, "Municipal Corporation (General) — Manual Review Required")


# ---------------------------------------------------------------------------
# SKILL 4: CSV I/O Handler
# ---------------------------------------------------------------------------

def classify_row(complaint_id: str, complaint_text: str) -> dict:
    """
    Runs all three classification skills on a single complaint row.
    Returns a dict with category, severity, department.
    """
    category   = detect_category(complaint_text)
    severity   = classify_severity(complaint_text)
    department = route_department(category)

    return {
        "complaint_id":   complaint_id,
        "complaint_text": complaint_text,
        "category":       category,
        "severity":       severity,
        "department":     department,
    }


def handle_csv(input_path: str, output_path: str, audit_log_path: str):
    """
    Skill 4 — handle_csv
    Reads input CSV, classifies every row, writes output CSV.
    Also writes an audit log for reviewer traceability.
    """
    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    results = []
    audit_lines = [
        f"# Audit Log — UC-0A Complaint Classifier",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Input: {input_path}",
        f"# Output: {output_path}",
        "",
    ]

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        # Detect column names flexibly
        fieldnames = reader.fieldnames or []
        id_col   = next((f for f in fieldnames if "id" in f.lower()),   fieldnames[0] if fieldnames else "complaint_id")
        text_col = next((f for f in fieldnames if "text" in f.lower() or "complaint" in f.lower()), fieldnames[1] if len(fieldnames) > 1 else "complaint_text")

        for i, row in enumerate(reader, start=1):
            complaint_id   = row.get(id_col, str(i)).strip()
            complaint_text = row.get(text_col, "").strip()

            if not complaint_text:
                # Never skip a row — write Unknown if blank
                result = {
                    "complaint_id":   complaint_id,
                    "complaint_text": complaint_text,
                    "category":       "Unknown",
                    "severity":       "Unknown",
                    "department":     "Unknown — Empty complaint text",
                }
                audit_lines.append(
                    f"[ROW {i:>4}] SKIPPED — empty complaint text (id={complaint_id})"
                )
            else:
                result = classify_row(complaint_id, complaint_text)
                audit_lines.append(
                    f'[ROW {i:>4}] TEXT: "{complaint_text[:80]}" '
                    f'→ CATEGORY: {result["category"]} '
                    f'| SEVERITY: {result["severity"]} '
                    f'| DEPT: {result["department"]}'
                )

            results.append(result)

    # Write output CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=["complaint_id", "complaint_text", "category", "severity", "department"]
        )
        writer.writeheader()
        writer.writerows(results)

    # Write audit log
    with open(audit_log_path, "w", encoding="utf-8") as logfile:
        logfile.write("\n".join(audit_lines))

    print(f"[OK] Classified {len(results)} complaints.")
    print(f"[OK] Results written to : {output_path}")
    print(f"[OK] Audit log written  : {audit_log_path}")

    # Print severity summary
    from collections import Counter
    severity_counts = Counter(r["severity"] for r in results)
    print("\n--- Severity Summary ---")
    for sev in ["Critical", "High", "Medium", "Low", "Unknown"]:
        count = severity_counts.get(sev, 0)
        if count:
            print(f"  {sev:<12}: {count}")

    category_counts = Counter(r["category"] for r in results)
    print("\n--- Category Summary ---")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:<30}: {count}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier — Nasscom Vibe Coding Workshop"
    )
    parser.add_argument(
        "--city",
        required=True,
        choices=["pune", "hyderabad", "kolkata", "ahmedabad"],
        help="City name (must match a test CSV in data/city-test-files/)"
    )
    args = parser.parse_args()

    city = args.city.lower()

    # Paths relative to repo root
    input_path    = os.path.join("data", "city-test-files", f"test_{city}.csv")
    output_path   = os.path.join("uc-0a", f"results_{city}.csv")
    audit_log_path = os.path.join("uc-0a", f"audit_{city}.txt")

    print(f"\n=== UC-0A Complaint Classifier ===")
    print(f"City   : {city}")
    print(f"Input  : {input_path}")
    print(f"Output : {output_path}\n")

    handle_csv(input_path, output_path, audit_log_path)


if __name__ == "__main__":
    main()
