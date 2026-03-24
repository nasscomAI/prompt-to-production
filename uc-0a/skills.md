"""
UC-0A Complaint Classifier
Implements classify_complaint and batch_classify as defined in skills.md.
Enforcement rules are drawn directly from agents.md.
"""

import argparse
import csv
import json
import sys
import traceback
from pathlib import Path

# ── Schema constants ────────────────────────────────────────────────────────

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}

OUTPUT_FIELDNAMES = ["complaint_id", "category", "priority", "reason", "flag"]

# ── Anthropic API call ───────────────────────────────────────────────────────

def _call_claude(description: str) -> dict:
    """
    Call the Anthropic API with a tightly constrained RICE prompt.
    Returns parsed JSON dict with keys: category, priority, reason, flag.
    """
    import urllib.request

    system_prompt = f"""You are a civic complaint classification agent. Classify the complaint and return ONLY a JSON object — no prose, no markdown fences.

ALLOWED CATEGORIES (use exact spelling): {", ".join(sorted(ALLOWED_CATEGORIES))}
ALLOWED PRIORITIES: Urgent, Standard, Low

RULES YOU MUST FOLLOW:
1. category — must be exactly one value from the allowed list above. No variations, no synonyms.
2. priority — set to Urgent if and only if the description contains ANY of these words (case-insensitive): {", ".join(sorted(SEVERITY_KEYWORDS))}. Otherwise Standard (clear mid-impact issue) or Low (nuisance/minor).
3. reason — exactly one sentence. Must quote at least one specific word or short phrase from the description verbatim. Explain the category and priority choice.
4. flag — set to "NEEDS_REVIEW" if the complaint is genuinely ambiguous between two categories, or if no category fits well. Otherwise leave as empty string "".
5. Never invent categories. If nothing fits, use Other + NEEDS_REVIEW.

Return exactly this JSON shape:
{{"category": "...", "priority": "...", "reason": "...", "flag": ""}}"""

    user_message = f"Classify this complaint:\n\n{description}"

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 300,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    raw_text = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            raw_text += block["text"]

    # Strip any accidental markdown fences
    clean = raw_text.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip().strip("`")

    return json.loads(clean)


# ── Local fallback classifier (used when API is unreachable) ─────────────────

# Maps (keyword_set, category) in priority order — first match wins
_CATEGORY_RULES = [
    ({"pothole", "pot hole"},                          "Pothole"),
    ({"flooding", "flooded", "flood", "waterlogged"},  "Flooding"),
    ({"streetlight", "street light", "street lamp",
      "lamp post", "light post"},                      "Streetlight"),
    ({"garbage", "waste", "debris", "litter",
      "trash", "dumped", "overflowing bin"},            "Waste"),
    ({"noise", "music", "loud", "loudspeaker",
      "sound", "midnight"},                             "Noise"),
    ({"heritage", "historic", "monument",
      "shaniwar", "peshwa"},                            "Heritage Damage"),
    ({"heat", "temperature", "shade", "summer",
      "heat stroke"},                                   "Heat Hazard"),
    ({"drain", "drainage", "manhole", "sewer",
      "blocked drain"},                                 "Drain Blockage"),
    ({"road damage", "asphalt", "cracked road",
      "buckled", "pothole"},                            "Road Damage"),
]

def _local_classify(description: str) -> dict:
    """
    Rule-based fallback used when the Anthropic API is unreachable.
    Applies keyword matching then severity checks.
    """
    lower = description.lower()
    category = "Other"
    flag = ""

    # Category matching
    matches = []
    for keywords, cat in _CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            matches.append(cat)

    if len(matches) == 1:
        category = matches[0]
    elif len(matches) > 1:
        category = matches[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority: severity keyword check
    triggered = [kw for kw in SEVERITY_KEYWORDS if kw in lower]
    if triggered:
        priority = "Urgent"
        reason = (
            f"Classified as {category} based on description keywords; "
            f"priority set to Urgent because description contains '{triggered[0]}'."
        )
    else:
        # Heuristic: "blocking", "unable", "dangerous" → Standard; else Low
        mid_impact = {"block", "unable", "dangerous", "swerve", "safety", "broken", "pooling"}
        if any(w in lower for w in mid_impact):
            priority = "Standard"
        else:
            priority = "Low"
        reason = f"Classified as {category} based on keywords in description; no severity terms found."

    return {"category": category, "priority": priority, "reason": reason, "flag": flag}


# ── Enforcement validator ────────────────────────────────────────────────────

def _enforce(row_id: str, description: str, result: dict) -> dict:
    """
    Apply hard enforcement rules from agents.md on top of the model output.
    Mutates result in place and returns it.
    """
    # Rule 1: category must be in allowed set
    if result.get("category") not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
        result["reason"] = (
            f"Model returned an invalid category; forced to Other. "
            f"Original description: '{description[:60]}...'"
        )

    # Rule 2: severity keyword → Urgent override
    lower_desc = description.lower()
    triggered = [kw for kw in SEVERITY_KEYWORDS if kw in lower_desc]
    if triggered:
        if result.get("priority") != "Urgent":
            result["priority"] = "Urgent"
            # Append note to reason if it doesn't already mention it
            if "urgent" not in result.get("reason", "").lower():
                result["reason"] = (
                    result.get("reason", "").rstrip(".") +
                    f" — auto-escalated to Urgent because description contains '{triggered[0]}'."
                )

    # Rule 3: priority must be in allowed set
    if result.get("priority") not in ALLOWED_PRIORITIES:
        result["priority"] = "Standard"

    # Rule 4: flag must be NEEDS_REVIEW or ""
    flag = result.get("flag", "")
    if flag not in ("NEEDS_REVIEW", ""):
        result["flag"] = "NEEDS_REVIEW"

    # Rule 5: reason must exist
    if not result.get("reason", "").strip():
        result["reason"] = f"No reason provided by model for complaint '{row_id}'."
        result["flag"] = "NEEDS_REVIEW"

    return result


# ── Public skill: classify_complaint ────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Input:  dict with keys complaint_id and description
    Output: dict with keys complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # Empty description fallback (skills.md error_handling)
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description was empty — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    try:
        result = _call_claude(description)
    except Exception:
        # API unreachable — use local rule-based fallback
        result = _local_classify(description)

    try:
        result = _enforce(complaint_id, description, result)
        result["complaint_id"] = complaint_id
        return result
    except Exception as exc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": f"Classification error: {type(exc).__name__}: {exc}",
            "flag": "NEEDS_REVIEW",
        }


# ── Public skill: batch_classify ────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes silently — bad rows are written with NEEDS_REVIEW.
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Processing {len(rows)} complaints from {input_path} ...")

    for i, row in enumerate(rows, 1):
        complaint_id = row.get("complaint_id", f"ROW_{i}")
        try:
            result = classify_complaint(row)
        except Exception as exc:
            result = {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": f"Batch error on row {i}: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

        # Progress indicator
        cat = result["category"]
        pri = result["priority"]
        flg = f" [{result['flag']}]" if result["flag"] else ""
        print(f"  [{i:02d}] {complaint_id:<10} → {cat:<18} {pri:<8}{flg}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in OUTPUT_FIELDNAMES})

    urgent_count = sum(1 for r in results if r["priority"] == "Urgent")
    review_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"\nSummary: {len(results)} rows | {urgent_count} Urgent | {review_count} NEEDS_REVIEW")


# ── Entrypoint ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
        print(f"\nDone. Results written to {args.output}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)