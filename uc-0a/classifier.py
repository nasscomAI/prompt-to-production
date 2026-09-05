"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md + skills.md.
"""
import argparse
import csv
import json
import os
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

_MODEL = "gemini-3.5-flash-lite"
_CONFIG = types.GenerateContentConfig(
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
)

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
}
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}
FALLBACK = {"category": "Other", "priority": "Low", "reason": "Classification unavailable", "flag": "NEEDS_REVIEW"}


def _load_env() -> None:
    """Load GEMINI_API_KEY from .env files if not already set."""
    if os.environ.get("GEMINI_API_KEY"):
        return

    candidates = [
        Path(__file__).resolve().parents[2] / ".env",  # nasscom/.env
        Path(__file__).resolve().parents[1] / ".env",  # prompt-to-production/.env
    ]
    for env_path in candidates:
        if not env_path.is_file():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value
        if os.environ.get("GEMINI_API_KEY"):
            return


def _get_client() -> genai.Client:
    _load_env()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Export it or add it to .env in the project root."
        )
    return genai.Client(api_key=api_key)


_client = None


def _client_instance() -> genai.Client:
    global _client
    if _client is None:
        _client = _get_client()
    return _client


def _has_severity(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in SEVERITY_KEYWORDS)


def _build_prompt(description: str, location: str) -> str:
    return f"""You are a civic complaint classifier. Classify the complaint below using ONLY these rules.

ALLOWED CATEGORIES (exact strings only): Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other

PRIORITY RULES:
- Urgent: description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive)
- Standard: active/ongoing problem, no severity keyword
- Low: minor inconvenience, cosmetic, or historical observation

FLAG RULES:
- Set flag to NEEDS_REVIEW if: description maps equally to 2+ categories, is too vague, or is unparseable
- When flag is NEEDS_REVIEW, category MUST be Other
- Otherwise flag is empty string

OUTPUT: Respond with ONLY a JSON object, no markdown, no explanation:
{{"category": "<exact category>", "priority": "<Urgent|Standard|Low>", "reason": "<one sentence quoting at least one word from description>", "flag": "<NEEDS_REVIEW or empty string>"}}

Location: {location}
Description: {description}"""


def _parse_llm_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


def _call_llm(description: str, location: str) -> dict:
    last_error = None
    for attempt in range(3):
        try:
            response = _client_instance().models.generate_content(
                model=_MODEL,
                contents=_build_prompt(description, location),
                config=_CONFIG,
            )
            result = _parse_llm_json(response.text)
            time.sleep(1)  # avoid free-tier rate limiting
            return result
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last_error


def classify_complaint(row: dict) -> dict:
    description = row.get("description") or ""
    location = row.get("location") or ""

    if not description or not description.strip():
        return {"category": "Other", "priority": "Low", "reason": "No description provided", "flag": "NEEDS_REVIEW"}
    if len(description.strip()) < 5:
        return {"category": "Other", "priority": "Low", "reason": "Description too short to classify", "flag": "NEEDS_REVIEW"}

    try:
        result = _call_llm(description, location)
    except Exception:
        return {**FALLBACK}

    # Validate category — retry once if invalid
    if result.get("category") not in ALLOWED_CATEGORIES:
        try:
            result = _call_llm(
                f"[CORRECTION REQUIRED] Category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}.\n\n" + description,
                location,
            )
        except Exception:
            return {**FALLBACK}
        if result.get("category") not in ALLOWED_CATEGORIES:
            result["category"] = "Other"
            result["flag"] = "NEEDS_REVIEW"

    # Validate reason — retry once if missing
    if not result.get("reason", "").strip():
        try:
            result = _call_llm(description, location)
        except Exception:
            return {**FALLBACK}
        if not result.get("reason", "").strip():
            result["reason"] = "Description insufficient to determine category"
            result["flag"] = "NEEDS_REVIEW"

    # Enforce: NEEDS_REVIEW → category must be Other
    if result.get("flag") == "NEEDS_REVIEW":
        result["category"] = "Other"

    # Enforce severity keyword → always Urgent (overrides LLM)
    if _has_severity(description):
        result["priority"] = "Urgent"
    elif result.get("priority") == "Urgent":
        # No severity keyword — Urgent is not allowed per agents.md
        result["priority"] = "Standard"

    # Normalise flag to empty string if not NEEDS_REVIEW
    if result.get("flag") != "NEEDS_REVIEW":
        result["flag"] = ""

    return {
        "category": result.get("category", "Other"),
        "priority": result.get("priority", "Low"),
        "reason": result.get("reason", ""),
        "flag": result.get("flag", ""),
    }


def batch_classify(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames or []
    except Exception as exc:
        raise ValueError(f"File is not valid CSV: {input_path}") from exc

    if "description" not in fieldnames:
        raise ValueError("Required column 'description' is absent from the CSV header")

    has_location = "location" in fieldnames
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if not os.path.isdir(out_dir) or not os.access(out_dir, os.W_OK):
        raise IOError(f"Output directory does not exist or is not writable: {out_dir}")

    out_fields = list(fieldnames) + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint({
                    "description": row.get("description", ""),
                    "location": row.get("location", "") if has_location else "",
                })
                if not isinstance(result, dict) or "category" not in result:
                    raise ValueError("Invalid result structure")
            except Exception:
                result = {"category": "Other", "priority": "Low", "reason": "Classification error on this row", "flag": "NEEDS_REVIEW"}
            writer.writerow({**row, **result})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
