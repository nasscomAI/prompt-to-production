"""
UC-0A — Civic Complaint Classifier
===================================
Reads  : data/city-test-files/test_hyderabad.csv
Writes : uc-0a/results_hyderabad.csv

CRAFT Loop
----------
C — Context  : Municipal complaint triage for Hyderabad civic body
R — Role     : CivicTriage Agent (see agents.md)
A — Action   : Classify each complaint → category, severity, suggested_action
F — Format   : CSV row per complaint
T — Test     : Run assertions at bottom; all must pass before PR

Usage
-----
    python uc-0a/classifier.py
"""

import csv
import os
import sys

# ──────────────────────────────────────────────────────────────
# SKILL 1 — Keyword-Based Category Routing
# ──────────────────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "Roads":       ["road", "pothole", "footpath", "pavement", "traffic",
                    "signal", "divider", "street", "crossing"],
    "Water":       ["water", "pipe", "leak", "supply", "drainage", "sewage",
                    "overflow", "tap", "borewell", "drain"],
    "Sanitation":  ["garbage", "waste", "dustbin", "litter", "sweeping",
                    "trash", "dump", "cleaning", "sanitation"],
    "Electricity": ["power", "electricity", "light", "streetlight", "wire",
                    "transformer", "outage", "shock", "electric"],
    "Parks":       ["park", "garden", "tree", "playground", "bench",
                    "grass", "bush", "shrub"],
    "Health":      ["hospital", "disease", "mosquito", "stagnant", "rats",
                    "hygiene", "smell", "epidemic", "fever", "pest",
                    "cockroach", "contaminated"],
}

# ──────────────────────────────────────────────────────────────
# SKILL 2 — Severity Escalation Detector
# ──────────────────────────────────────────────────────────────
HIGH_SEVERITY_TRIGGERS = {
    "injury", "injured", "accident", "child", "children", "school",
    "hospital", "fire", "flood", "collapse", "danger", "dangerous",
    "emergency", "death", "dead", "unsafe", "bleeding", "electrocuted",
    "electrocution",
}

# ──────────────────────────────────────────────────────────────
# SKILL 3 — Baseline Severity Scorer
# ──────────────────────────────────────────────────────────────
MEDIUM_SIGNALS = [
    "days", "week", "weeks", "month", "months", "area", "locality",
    "colony", "neighbourhood", "neighborhood", "residents", "households",
    "everyone", "all houses", "entire", "whole street",
]


def classify_category(text: str) -> str:
    """Skill 1: Map complaint text to department category."""
    lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return category
    return "Other"


def classify_severity(text: str) -> str:
    """Skills 2 & 3: Determine severity level."""
    lower = text.lower()
    words = set(lower.split())

    # Skill 2 — high trigger check (word-level + substring for compound words)
    for trigger in HIGH_SEVERITY_TRIGGERS:
        if trigger in lower:
            return "High"

    # Skill 3 — medium vs low
    if any(signal in lower for signal in MEDIUM_SIGNALS):
        return "Medium"

    return "Low"


def suggest_action(category: str, severity: str, text: str) -> str:
    """Skill 4: Generate a specific, actionable one-liner for field teams."""
    urgency = {
        "High":   "immediately",
        "Medium": "within 24 hours",
        "Low":    "at the next scheduled visit",
    }[severity]

    templates = {
        "Roads":       f"Dispatch road repair crew to inspect and fix the reported issue {urgency}",
        "Water":       f"Send plumbing team to inspect water supply or drainage fault {urgency}",
        "Sanitation":  f"Schedule garbage collection and area cleaning {urgency}",
        "Electricity": f"Alert DISCOM to repair electrical fault or streetlight issue {urgency}",
        "Parks":       f"Assign parks maintenance crew to address reported issue {urgency}",
        "Health":      f"Notify health inspectors and arrange pest control or fogging {urgency}",
        "Other":       f"Log complaint and assign duty officer for on-ground assessment {urgency}",
    }
    return templates.get(category, templates["Other"])


def classify_complaint(complaint_text: str) -> dict:
    """Full classification pipeline for one complaint."""
    category = classify_category(complaint_text)
    severity = classify_severity(complaint_text)
    action   = suggest_action(category, severity, complaint_text)
    return {
        "category":         category,
        "severity":         severity,
        "suggested_action": action,
    }


# ──────────────────────────────────────────────────────────────
# SKILL 5 — CSV Row Emitter (main pipeline)
# ──────────────────────────────────────────────────────────────
def run(input_path: str, output_path: str) -> None:
    """Read input CSV, classify each complaint, write results CSV."""
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found → {input_path}")
        print("Make sure you have cloned the full repo and data files are present.")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Accept flexible column naming
        fieldnames = reader.fieldnames or []
        id_col   = next((c for c in fieldnames if "id"       in c.lower()), None)
        text_col = next((c for c in fieldnames if "complaint" in c.lower()
                         or "text" in c.lower() or "description" in c.lower()), None)

        if not text_col:
            print(f"ERROR: Could not find a complaint text column in {input_path}")
            print(f"       Available columns: {fieldnames}")
            sys.exit(1)

        for row in reader:
            text   = row[text_col].strip()
            result = classify_complaint(text)
            out_row = {}
            if id_col:
                out_row["complaint_id"] = row[id_col]
            out_row["complaint_text"]   = text
            out_row.update(result)
            results.append(out_row)

    out_fields = (["complaint_id"] if id_col else []) + [
        "complaint_text", "category", "severity", "suggested_action"
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"✅  Classified {len(results)} complaints → {output_path}")


# ──────────────────────────────────────────────────────────────
# CRAFT Tests — must all pass before raising PR
# ──────────────────────────────────────────────────────────────
def run_tests() -> None:
    """Inline test suite covering all CRAFT failure modes."""
    print("\n── Running CRAFT tests ──")
    failures = []

    def check(name, got, expected):
        if got != expected:
            failures.append(f"  FAIL [{name}]: expected '{expected}', got '{got}'")
        else:
            print(f"  PASS  {name}")

    # Category routing
    check("Roads",       classify_category("There is a big pothole on the main road"), "Roads")
    check("Water",       classify_category("Water pipe burst near our colony"),        "Water")
    check("Sanitation",  classify_category("Garbage not collected for 5 days"),        "Sanitation")
    check("Electricity", classify_category("Streetlight not working since Monday"),    "Electricity")
    check("Parks",       classify_category("Tree fell in the park"),                   "Parks")
    check("Health",      classify_category("Mosquito breeding in stagnant water"),     "Health")
    check("Other",       classify_category("Please help with my complaint"),            "Other")

    # Severity — High triggers (the key bug this CRAFT loop fixes)
    check("High-child",    classify_severity("Pothole near school, child almost fell"),     "High")
    check("High-injury",   classify_severity("Worker got injured due to open manhole"),     "High")
    check("High-hospital", classify_severity("No water supply near hospital"),              "High")
    check("High-unsafe",   classify_severity("Electric wire hanging low, very unsafe"),     "High")
    check("High-flood",    classify_severity("Flood water entering homes"),                  "High")

    # Severity — Medium
    check("Medium-days",   classify_severity("No electricity for 3 days in this area"),    "Medium")
    check("Medium-colony", classify_severity("Garbage pile in the entire colony"),         "Medium")

    # Severity — Low
    check("Low-basic",     classify_severity("Bench in park is broken"),                   "Low")

    if failures:
        print("\n── Test Failures ──")
        for f in failures:
            print(f)
        sys.exit(1)
    else:
        print("\n✅  All tests passed — safe to commit and raise PR\n")


# ──────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Paths relative to repo root — run from there:  python uc-0a/classifier.py
    INPUT_PATH  = os.path.join("data", "city-test-files", "test_hyderabad.csv")
    OUTPUT_PATH = os.path.join("uc-0a", "results_hyderabad.csv")

    run_tests()
    run(INPUT_PATH, OUTPUT_PATH)
