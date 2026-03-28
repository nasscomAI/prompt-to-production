"""
UC-0A: Complaint Classifier
Nasscom AI Code Sarathi — Prompt to Production Workshop

Usage:
    python classifier.py --city <city_name>

Example:
    python classifier.py --city hyderabad

The script reads:
    data/city-test-files/test_<city>.csv

And writes:
    uc-0a/results_<city>.csv

Requirements:
    pip install anthropic
    Set ANTHROPIC_API_KEY environment variable before running.
"""

import csv
import json
import os
import sys
import argparse
import time

try:
    import anthropic
except ImportError:
    print("ERROR: 'anthropic' package not found. Run: pip install anthropic")
    sys.exit(1)


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

MODEL = "claude-sonnet-4-20250514"

VALID_CATEGORIES = {
    "ROADS", "SANITATION", "WATER", "ELECTRICITY",
    "NOISE", "PUBLIC_SAFETY", "ENVIRONMENT", "OTHER"
}

VALID_SEVERITIES = {"HIGH", "MEDIUM", "LOW"}

HIGH_SEVERITY_KEYWORDS = [
    "injury", "injured", "accident", "child", "children",
    "school", "hospital", "fire", "death", "died",
    "collapsed", "electric shock", "live wire", "open wire",
    "contaminated", "sick", "sewage overflow"
]

SYSTEM_PROMPT = """You are a civic complaint classification agent for Indian municipal corporations.

Your job: Given a citizen complaint text, return ONLY a JSON object with three fields:
- "category": one of ROADS | SANITATION | WATER | ELECTRICITY | NOISE | PUBLIC_SAFETY | ENVIRONMENT | OTHER
- "severity": one of HIGH | MEDIUM | LOW
- "reason": one sentence explaining your decision

CATEGORY GUIDE:
- ROADS: Potholes, road damage, broken footpaths, missing manholes, road flooding
- SANITATION: Garbage not collected, open dumping, overflowing bins, drain blockage
- WATER: No water supply, low pressure, contaminated water, pipeline burst/leak
- ELECTRICITY: Power outage, broken streetlight, fallen wire, meter issue
- NOISE: Loud music, construction noise at night, loudspeaker violations
- PUBLIC_SAFETY: Stray animals, unsafe structures, crime hotspot, dangerous open pits
- ENVIRONMENT: Illegal construction, tree cutting, air/water pollution, encroachment
- OTHER: Does not fit any category above

SEVERITY GUIDE:
- HIGH: Risk to human life. Triggers: injury, accident, child, school, hospital, fire, death, collapsed, electric shock, open wire, contaminated drinking water, sewage overflow near homes
- MEDIUM: Ongoing civic issue causing significant inconvenience but no immediate danger
- LOW: Minor or cosmetic issue; inconvenient but not harmful

RULES:
1. Return ONLY valid JSON — no extra text, no markdown, no explanation outside the JSON.
2. category must be exactly one of the 8 values listed above.
3. severity must be exactly HIGH, MEDIUM, or LOW.
4. reason must be one plain English sentence.
5. If complaint mentions injury, child, hospital, school, or life-threatening conditions → severity MUST be HIGH.

Example output:
{"category": "ROADS", "severity": "HIGH", "reason": "Pothole caused accident and injury was reported."}
"""


# ─────────────────────────────────────────────
# Helper: keyword-based severity override
# ─────────────────────────────────────────────

def has_high_severity_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in HIGH_SEVERITY_KEYWORDS)


# ─────────────────────────────────────────────
# Core classification function
# ─────────────────────────────────────────────

def classify_complaint(client: anthropic.Anthropic, complaint_text: str) -> dict:
    """
    Calls the Claude API to classify a single complaint.
    Returns dict with keys: category, severity, reason
    Falls back gracefully on parse errors.
    """
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Classify this complaint:\n\n{complaint_text}"}
            ]
        )

        raw = response.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)

        # Validate category
        category = result.get("category", "OTHER").upper()
        if category not in VALID_CATEGORIES:
            category = "OTHER"

        # Validate severity
        severity = result.get("severity", "MEDIUM").upper()
        if severity not in VALID_SEVERITIES:
            severity = "MEDIUM"

        # Enforcement: keyword-based HIGH override
        if has_high_severity_keywords(complaint_text) and severity != "HIGH":
            severity = "HIGH"
            result["reason"] = result.get("reason", "") + " [Severity escalated to HIGH due to safety keywords.]"

        reason = result.get("reason", "Classification based on complaint content.")

        return {
            "category": category,
            "severity": severity,
            "reason": reason
        }

    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON parse error: {e}. Falling back to defaults.")
        severity = "HIGH" if has_high_severity_keywords(complaint_text) else "MEDIUM"
        return {
            "category": "OTHER",
            "severity": severity,
            "reason": "Could not parse model response; classified as OTHER."
        }
    except Exception as e:
        print(f"  [ERROR] API call failed: {e}")
        return {
            "category": "OTHER",
            "severity": "MEDIUM",
            "reason": f"Error during classification: {str(e)}"
        }


# ─────────────────────────────────────────────
# CSV processing
# ─────────────────────────────────────────────

def process_city(city: str):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("  Set it with: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Resolve input path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    input_path = os.path.join(repo_root, "data", "city-test-files", f"test_{city}.csv")

    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found: {input_path}")
        print(f"  Make sure the file exists at: data/city-test-files/test_{city}.csv")
        sys.exit(1)

    output_path = os.path.join(script_dir, f"results_{city}.csv")

    print(f"\n{'='*55}")
    print(f"  UC-0A Complaint Classifier")
    print(f"  City     : {city}")
    print(f"  Input    : {input_path}")
    print(f"  Output   : {output_path}")
    print(f"{'='*55}\n")

    results = []
    errors = 0

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        # Detect column names flexibly
        fieldnames = reader.fieldnames or []
        id_col = next((f for f in fieldnames if "id" in f.lower()), None)
        text_col = next(
            (f for f in fieldnames if any(k in f.lower() for k in ["complaint", "text", "description", "issue"])),
            None
        )

        if not text_col:
            print(f"ERROR: Could not find a complaint text column in: {fieldnames}")
            print("  Expected a column with 'complaint', 'text', 'description', or 'issue' in its name.")
            sys.exit(1)

        rows = list(reader)

    print(f"  Found {len(rows)} complaint(s) to classify.\n")

    for i, row in enumerate(rows, 1):
        complaint_id = row.get(id_col, str(i)) if id_col else str(i)
        complaint_text = row.get(text_col, "").strip()

        if not complaint_text:
            print(f"  [{i}/{len(rows)}] ID={complaint_id} — SKIPPED (empty text)")
            results.append({
                "complaint_id": complaint_id,
                "complaint_text": complaint_text,
                "category": "OTHER",
                "severity": "LOW",
                "reason": "Empty complaint text."
            })
            continue

        print(f"  [{i}/{len(rows)}] Classifying ID={complaint_id}...")
        classification = classify_complaint(client, complaint_text)
        print(f"           → {classification['category']} | {classification['severity']}")

        results.append({
            "complaint_id": complaint_id,
            "complaint_text": complaint_text,
            "category": classification["category"],
            "severity": classification["severity"],
            "reason": classification["reason"]
        })

        # Brief pause to respect rate limits
        if i < len(rows):
            time.sleep(0.5)

    # Write output CSV
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=["complaint_id", "complaint_text", "category", "severity", "reason"]
        )
        writer.writeheader()
        writer.writerows(results)

    # Summary
    total = len(results)
    high = sum(1 for r in results if r["severity"] == "HIGH")
    medium = sum(1 for r in results if r["severity"] == "MEDIUM")
    low = sum(1 for r in results if r["severity"] == "LOW")

    print(f"\n{'='*55}")
    print(f"  Done! Results saved to: {output_path}")
    print(f"  Total classified : {total}")
    print(f"  HIGH severity    : {high}")
    print(f"  MEDIUM severity  : {medium}")
    print(f"  LOW severity     : {low}")
    print(f"{'='*55}\n")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A: Civic Complaint Classifier using Claude AI"
    )
    parser.add_argument(
        "--city",
        required=True,
        help="City name matching the test CSV, e.g. hyderabad, pune, kolkata, ahmedabad"
    )
    args = parser.parse_args()
    process_city(args.city.lower())
