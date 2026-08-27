"""
UC-0A — Complaint Classifier
Classifies civic complaints using Claude with RICE enforcement rules from agents.md.
"""
import argparse
import csv
import json
import sys
import anthropic

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

SYSTEM_PROMPT = """You are a municipal complaint classifier for a city corporation.

ROLE: Classify each citizen complaint into exactly one category, assign a priority, provide a reason, and flag ambiguous cases. You do not act on complaints — you only classify them.

INTENT: For every complaint, produce: category, priority, reason, flag. A correct output uses only exact allowed values and never invents new ones.

CONTEXT: Classify using the description text only. Do not use complaint_id, ward name, date, or reporter identity.

ENFORCEMENT RULES:
1. category MUST be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
   No variations, abbreviations, or sub-categories allowed.
2. priority MUST be "Urgent" if the description contains any of these words (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
   Otherwise use "Standard" for active ongoing issues or "Low" for minor or cosmetic issues.
3. reason MUST be exactly one sentence directly quoting or closely paraphrasing the specific words from the description that drove the category and priority decision.
4. flag MUST be "NEEDS_REVIEW" when the description could reasonably belong to two or more categories with equal weight. Leave flag as empty string when classification is clear.
5. If category cannot be determined from the description alone, use category "Other" and flag "NEEDS_REVIEW". Never invent a category outside the allowed list."""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "classifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "complaint_id": {"type": "string"},
                    "category": {"type": "string"},
                    "priority": {"type": "string"},
                    "reason": {"type": "string"},
                    "flag": {"type": "string"},
                },
                "required": ["complaint_id", "category", "priority", "reason", "flag"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["classifications"],
    "additionalProperties": False,
}


def _enforce(result: dict, description: str) -> dict:
    if result.get("category") not in ALLOWED_CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"
    if result.get("priority") not in ("Urgent", "Standard", "Low"):
        result["priority"] = "Standard"
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in SEVERITY_KEYWORDS):
        result["priority"] = "Urgent"
    if not result.get("flag"):
        result["flag"] = ""
    return result


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row. Returns dict with complaint_id, category, priority, reason, flag."""
    client = anthropic.Anthropic()
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description field missing",
            "flag": "NEEDS_REVIEW",
        }

    prompt = (
        f"Classify this complaint and return a JSON object with keys: "
        f"complaint_id, category, priority, reason, flag.\n\n"
        f"complaint_id: {complaint_id}\n"
        f"description: {description}"
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=512,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            output_config={
                "format": {
                    "type": "json_schema",
                    "name": "complaint_classification",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "complaint_id": {"type": "string"},
                            "category": {"type": "string"},
                            "priority": {"type": "string"},
                            "reason": {"type": "string"},
                            "flag": {"type": "string"},
                        },
                        "required": ["complaint_id", "category", "priority", "reason", "flag"],
                        "additionalProperties": False,
                    },
                }
            },
            messages=[{"role": "user", "content": prompt}],
        )
        text = next(b.text for b in response.content if b.type == "text")
        result = json.loads(text)
        result["complaint_id"] = complaint_id
    except Exception as exc:
        print(f"  Warning: API error for {complaint_id}: {exc}", file=sys.stderr)
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Classification failed due to API error",
            "flag": "NEEDS_REVIEW",
        }

    return _enforce(result, description)


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify all rows in one API call, write results CSV."""
    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print("No rows found in input file.", file=sys.stderr)
        return

    print(f"Classifying {len(rows)} complaints...")

    rows_with_desc = [r for r in rows if r.get("description", "").strip()]
    rows_missing = [r for r in rows if not r.get("description", "").strip()]

    results_map: dict[str, dict] = {}

    for r in rows_missing:
        cid = r.get("complaint_id", "")
        results_map[cid] = {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description field missing",
            "flag": "NEEDS_REVIEW",
        }

    if rows_with_desc:
        complaints_text = "\n\n".join(
            f"complaint_id: {r['complaint_id']}\ndescription: {r['description']}"
            for r in rows_with_desc
        )
        prompt = (
            f"Classify all of the following complaints. "
            f"Return a JSON object with key 'classifications' containing an array, "
            f"one element per complaint, each with: complaint_id, category, priority, reason, flag.\n\n"
            f"{complaints_text}"
        )

        client = anthropic.Anthropic()
        try:
            response = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=4096,
                thinking={"type": "adaptive"},
                system=SYSTEM_PROMPT,
                output_config={"format": {"type": "json_schema", "name": "batch_classifications", "schema": OUTPUT_SCHEMA}},
                messages=[{"role": "user", "content": prompt}],
            )
            text = next(b.text for b in response.content if b.type == "text")
            data = json.loads(text)
            classifications = data.get("classifications", [])
        except Exception as exc:
            print(f"Batch API call failed: {exc}", file=sys.stderr)
            print("Falling back to per-row classification...", file=sys.stderr)
            classifications = []
            for r in rows_with_desc:
                classifications.append(classify_complaint(r))

        desc_by_id = {r["complaint_id"]: r.get("description", "") for r in rows_with_desc}
        for item in classifications:
            cid = item.get("complaint_id", "")
            desc = desc_by_id.get(cid, "")
            results_map[cid] = _enforce(item, desc)

        classified_ids = {item.get("complaint_id") for item in classifications}
        for r in rows_with_desc:
            cid = r["complaint_id"]
            if cid not in classified_ids:
                print(f"  Warning: no classification returned for {cid}, falling back.", file=sys.stderr)
                results_map[cid] = classify_complaint(r)

    ordered = [results_map.get(r["complaint_id"], {
        "complaint_id": r["complaint_id"],
        "category": "Other",
        "priority": "Standard",
        "reason": "Classification missing from API response",
        "flag": "NEEDS_REVIEW",
    }) for r in rows]

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(ordered)

    print(f"Classified {len(ordered)} complaints → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
