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

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 300,
        "system": system_prompt,
        "messages": [{"role": "user", "content": f"Classify this complaint:\n\n{description}"}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={"Content-Type": "application/json", "anthropic-version": "2023-06-01"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    raw_text = "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
    clean = raw_text.strip().strip("`")
    if clean.startswith("json"):
        clean = clean[4:].strip()
    return json.loads(clean)


# ── Local fallback classifier ────────────────────────────────────────────────
# Maps (keyword_set, category) — first match wins, multiple matches → NEEDS_REVIEW

_CATEGORY_RULES = [
    ({"pothole", "pot hole", "tyre damage"},                         "Pothole"),
    ({"flood", "flooding", "flooded", "waterlogged", "knee-deep",
      "standing in water"},                                           "Flooding"),
    ({"heritage", "historic", "monument", "heritage street",
      "old city", "rasta peth"},                                      "Heritage Damage"),
    ({"streetlight", "street light", "street lamp", "lamp post",
      "light post", "flickering", "sparking",
      "consecutive streetlights"},                                    "Streetlight"),
    ({"garbage", "waste", "debris", "litter", "trash",
      "dumped", "overflowing bin", "dead animal",
      "animal not removed", "bulk waste"},                            "Waste"),
    ({"noise", "music", "loud", "loudspeaker", "sound", "midnight"}, "Noise"),
    ({"heat", "temperature", "shade", "summer", "heat stroke"},      "Heat Hazard"),
    ({"drain", "drainage", "manhole", "sewer", "blocked drain"},     "Drain Blockage"),
    ({"road damage", "asphalt", "cracked road", "buckled",
      "cracked and sinking", "sinking", "road surface",
      "footpath", "tiles broken", "upturned", "utility work",
      "pavement"},                                                    "Road Damage"),
]

# Flooding + Drain Blockage co-occurrence is a known ambiguity — flag but pick Flooding
_FLOOD_DRAIN_PAIR = {"Flooding", "Drain Blockage"}


def _extract_quote(description: str, keywords: list) -> str:
    """Return the first matched keyword in its original casing from description."""
    lower = description.lower()
    for kw in keywords:
        idx = lower.find(kw)
        if idx >= 0:
            return description[idx:idx + len(kw)]
    return keywords[0] if keywords else ""


def _local_classify(description: str) -> dict:
    """
    Rule-based fallback used when the Anthropic API is unreachable.
    Reasons quote specific words from the description.
    """
    lower = description.lower()
    flag = ""

    # Find all matching categories
    matches = []
    for keywords, cat in _CATEGORY_RULES:
        hit_kws = [kw for kw in keywords if kw in lower]
        if hit_kws:
            matches.append((cat, hit_kws))

    if len(matches) == 0:
        category = "Other"
        quote = description.split()[0]
        flag = "NEEDS_REVIEW"
    elif len(matches) == 1:
        category, hit_kws = matches[0]
        quote = _extract_quote(description, hit_kws)
    else:
        cats = {m[0] for m in matches}
        # Known acceptable overlap: Flooding + Drain — pick Flooding, flag it
        if cats == _FLOOD_DRAIN_PAIR:
            category = "Flooding"
            hit_kws = matches[0][1]
            flag = "NEEDS_REVIEW"
        else:
            category, hit_kws = matches[0]
            flag = "NEEDS_REVIEW"
        quote = _extract_quote(description, hit_kws)

    # Severity keyword check
    triggered = [kw for kw in SEVERITY_KEYWORDS if kw in lower]
    if triggered:
        sev_quote = _extract_quote(description, triggered)
        priority = "Urgent"
        reason = (
            f"Classified as {category} because description mentions '{quote}'; "
            f"priority Urgent because description contains '{sev_quote}'."
        )
    else:
        mid_impact = {
            "block", "unable", "dangerous", "swerve", "safety", "broken",
            "pooling", "stranded", "sparking", "flickering", "standing in water",
            "inaccessible", "very dark", "very dark", "out for", "no light"
        }
        priority = "Standard" if any(w in lower for w in mid_impact) else "Low"
        reason = (
            f"Classified as {category} because description mentions '{quote}'; "
            f"no severity keywords found, priority set to {priority}."
        )

    return {"category": category, "priority": priority, "reason": reason, "flag": flag}


# ── Enforcement validator ────────────────────────────────────────────────────

def _enforce(row_id: str, description: str, result: dict) -> dict:
    """Post-hoc hard enforcement of agents.md rules — runs on both API and fallback output."""

    # Rule 1: category must be in allowed set
    if result.get("category") not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
        result["reason"] = (
            f"Model returned an invalid category; forced to Other. "
            f"Original: '{description[:60]}...'"
        )

    # Rule 2: severity keyword → Urgent (cannot be overridden by model/fallback)
    lower_desc = description.lower()
    triggered = [kw for kw in SEVERITY_KEYWORDS if kw in lower_desc]
    if triggered and result.get("priority") != "Urgent":
        result["priority"] = "Urgent"
        if "urgent" not in result.get("reason", "").lower():
            sev_quote = _extract_quote(description, triggered)
            result["reason"] = (
                result.get("reason", "").rstrip(".") +
                f" — auto-escalated to Urgent because description contains '{sev_quote}'."
            )

    # Rule 3: priority in allowed set
    if result.get("priority") not in ALLOWED_PRIORITIES:
        result["priority"] = "Standard"

    # Rule 4: flag must be NEEDS_REVIEW or ""
    if result.get("flag", "") not in ("NEEDS_REVIEW", ""):
        result["flag"] = "NEEDS_REVIEW"

    # Rule 5: reason must exist
    if not result.get("reason", "").strip():
        result["reason"] = f"No reason provided for complaint '{row_id}'."
        result["flag"] = "NEEDS_REVIEW"

    return result


# ── Public skill: classify_complaint ────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

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
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Processing {len(rows)} complaints from {input_path} ...")
    results = []

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
        flg = f" [{result['flag']}]" if result["flag"] else ""
        print(f"  [{i:02d}] {complaint_id:<12} → {result['category']:<18} {result['priority']:<8}{flg}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in OUTPUT_FIELDNAMES})

    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    review = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"\nSummary: {len(results)} rows | {urgent} Urgent | {review} NEEDS_REVIEW")


# ── Entrypoint ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        batch_classify(args.input, args.output)
        print(f"\nDone. Results written to {args.output}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        traceback.print_exc()
        sys.exit(1)