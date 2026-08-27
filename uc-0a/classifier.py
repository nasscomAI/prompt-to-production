"""
UC-0A — Complaint Classifier

LLM-based classification (OpenAI chat completions) wrapped in a deterministic
enforcement layer so that every output row conforms exactly to the schema in
README.md:

  category : exact string from the allowed list (no variations)
  priority : Urgent | Standard | Low  (Urgent FORCED when any severity
             keyword appears in the description)
  reason   : exactly ONE sentence citing specific words from the description
  flag     : "" or NEEDS_REVIEW (only on genuine ambiguity / no fit)

The LLM proposes; the code disposes. Even if the model drifts, the
post-validation layer repairs the row before it is written.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Single source of truth — referenced EXACTLY as in README.md. Do not vary.
# ---------------------------------------------------------------------------
ALLOWED_CATEGORIES = [
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
ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]
FLAG_NEEDS_REVIEW = "NEEDS_REVIEW"
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
_MAX_ATTEMPTS = 3

_SYSTEM_PROMPT = """You are a municipal complaint classifier for Indian city ward operations. \
Classify ONE citizen complaint using ONLY the words in its description text. Do not use \
any other field and do not invent facts.

Return STRICT JSON with exactly these keys:
{"category": "...", "priority": "...", "reason": "...", "flag": "..."}

RULES

1) category MUST be EXACTLY one of these ten strings, character for character, with no \
plurals, synonyms or sub-categories:
   Pothole | Flooding | Streetlight | Waste | Noise | Road Damage | Heritage Damage | \
Heat Hazard | Drain Blockage | Other

   Definitions and precedence (apply in this order):
   - Pothole: hole(s)/crater(s) in the road surface.
   - Drain Blockage: drain/stormwater explicitly described as blocked or clogged. When an \
explicitly blocked drain AND resulting flooding are both stated, classify Drain Blockage as \
the root cause AND set flag to "NEEDS_REVIEW" because Flooding also fits.
   - Flooding: water accumulating/flooding public areas, or water/run-off discharged or \
channelled onto roads/public areas, where no explicit drain blockage is stated.
   - Streetlight: streetlights/lamp posts/lighting out, flickering, sparking, damaged or \
dark areas due to lighting failure — even if located in a heritage area.
   - Waste: garbage, waste dumping, overflowing bins, dead animals, market waste — even in \
a heritage zone.
   - Noise: loud music, amplifiers, construction drilling, engine idling nuisance.
   - Road Damage: other road/footpath surface defects — cracks, sinking, subsidence, \
buckling, broken tiles, missing manhole covers, collapsed road sections.
   - Heritage Damage: physical damage to heritage fabric (heritage lamp post knocked over, \
historic cobblestones broken up, heritage building defaced, heritage stone removed).
   - Heat Hazard: heat-caused dangers to people — melting/bubbling surfaces at high \
temperature, dangerously hot structures, harmful sun/heat exposure. Heat damage to \
vegetation/amenities with no danger to people is NOT Heat Hazard (e.g. grass dying or a \
broken irrigation system is maintenance, not a Heat Hazard).
   - Other + flag NEEDS_REVIEW: nothing above fits.

2) priority MUST be EXACTLY one of: Urgent | Standard | Low
   - HARD RULE: if the description contains ANY of these keywords (case-insensitive \
substring): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — \
then priority MUST be "Urgent".
   - EQUALLY HARD RULE: if NONE of those keywords appears anywhere in the description, \
priority MUST NOT be "Urgent" — choose "Standard" for ongoing public impact/safety \
concerns, or "Low" for minor/cosmetic issues.

3) reason: EXACTLY ONE sentence that quotes a specific phrase copied verbatim from the \
description and connects it to the classification (the category and why this priority). \
Never more than one sentence. No invented details.

4) flag: "NEEDS_REVIEW" ONLY in exactly two situations: (a) no allowed category fits so \
you chose "Other", or (b) the description explicitly states flooding AND explicitly states \
a blocked/clogged drain, so two categories fit equally. In ALL other cases flag MUST be "" \
(empty string), even when the complaint is serious."""


def _load_env() -> None:
    """Load OPENAI_API_KEY etc. from the repo-root .env if not already set."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI()
    return _client


_client = None


def _find_severity_keywords(text: str) -> list:
    lowered = text.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in lowered]


def _call_llm(description: str) -> dict:
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        timeout=60,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    'Classify this complaint description. Return ONLY the JSON object.\n'
                    f"description: {description}"
                ),
            },
        ],
    )
    content = response.choices[0].message.content or ""
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("LLM did not return a JSON object")
    return data


def _build_reason(category: str, description: str, keywords: list,
                  priority: str) -> str:
    """Deterministic one-sentence reason citing words actually in the description."""
    quote = ""
    if keywords:
        quote = keywords[0]
    else:
        tokens = [t for t in re.findall(r"[A-Za-z]{4,}", description)]
        quote = tokens[0].lower() if tokens else description[:40]
    base = f"Classified {category} based on '{quote}' quoted from the complaint description"
    if keywords and priority == "Urgent":
        base += f"; urgent because '{keywords[0]}' indicates a severity condition"
    return base + "."


def _sanitize_reason(reason: str, category: str, description: str,
                     keywords: list, priority: str) -> str:
    """Ensure exactly ONE sentence that cites words present in the description."""
    reason = re.sub(r"\s+", " ", (reason or "").strip())
    body = reason[:-1] if reason.endswith((".", "!", "?")) else reason
    single_sentence = bool(reason) and not re.search(r"[.!?]", body)
    desc_lower = description.lower()
    cited = any(w.lower() in desc_lower and len(w) >= 3
                for w in re.findall(r"[A-Za-z]+", reason))
    if single_sentence and cited:
        return reason
    return _build_reason(category, description, keywords, priority)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()
    keywords = _find_severity_keywords(description)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Urgent" if keywords else "Standard",
            "reason": "No description provided so no category evidence exists.",
            "flag": FLAG_NEEDS_REVIEW,
        }

    data = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            data = _call_llm(description)
            break
        except Exception as exc:
            print(f"[warn] {complaint_id}: LLM attempt {attempt + 1} failed: {exc}",
                  file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    if data is None:
        data = {}

    category = str(data.get("category", "")).strip()
    flag = str(data.get("flag", "")).strip()

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = FLAG_NEEDS_REVIEW

    priority = str(data.get("priority", "")).strip()
    if priority not in ALLOWED_PRIORITIES:
        priority = "Urgent" if keywords else "Standard"

    # Deterministic enforcement: severity keyword => Urgent, always.
    if keywords and priority != "Urgent":
        priority = "Urgent"
    # And no keyword => never Urgent (keeps priority fully deterministic).
    if not keywords and priority == "Urgent":
        priority = "Standard"

    # Flag hygiene: NEEDS_REVIEW or blank only; Other must always be flagged.
    # Deterministic flag logic (overrides model noise):
    #   - Other            => NEEDS_REVIEW
    #   - flooding AND an explicitly blocked/clogged drain => NEEDS_REVIEW
    #   - everything else  => blank
    flood_hit = re.search(r"flood|waterlogg", description.lower())
    block_hit = re.search(r"block|clog", description.lower())
    if category == "Other" or (flood_hit and block_hit):
        flag = FLAG_NEEDS_REVIEW
    else:
        flag = ""

    reason = _sanitize_reason(str(data.get("reason", "")).strip(), category,
                              description, keywords, priority)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    with open(input_path, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for index, row in enumerate(reader, start=1):
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                print(f"[error] row {index}: unexpected failure: {exc}",
                      file=sys.stderr)
                cid = (row.get("complaint_id") or "").strip() or f"ROW-{index}"
                results.append({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification failed so this row needs manual review.",
                    "flag": FLAG_NEEDS_REVIEW,
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows.")


if __name__ == "__main__":
    _load_env()
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
