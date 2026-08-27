"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and ambiguity flag.
Strategy: LLM-first (Groq or Gemini) with regex fallback if API is unavailable.
"""
import argparse
import csv
import json
import os
import re

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injur", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collaps",
]

# Keyword patterns mapped to categories (checked in order) — used as fallback
CATEGORY_RULES = [
    ("Pothole",        [r"\bpotholes?\b"]),
    ("Flooding",       [r"\bflood", r"\bwaterlog", r"\bsubmerg", r"\bstrand"]),
    ("Streetlight",    [r"\bstreetlights?\b", r"\bstreet\s*lights?\b", r"\blights?\s+out\b",
                        r"\bflicker", r"\blamp\s*posts?\b", r"\bunlit\b"]),
    ("Drain Blockage", [r"\bdrain", r"\bmanhole\b", r"\bsewer\b", r"\bblockage\b"]),
    ("Waste",          [r"\bgarbage\b", r"\bwaste\b", r"\bdump", r"\brefuse\b",
                        r"\btrash\b", r"\boverflowing\b", r"\bdead\s+animal\b",
                        r"\bnot\s+removed\b"]),
    ("Noise",          [r"\bnoise\b", r"\bloud\b", r"\bmusic\b", r"\bmidnight\b",
                        r"\bdecibel\b", r"\bdrilling\b", r"\bband\s+play"]),
    ("Road Damage",    [r"\broad\s+(surface|crack|damag|sinking|broken|collaps|subsid)\b",
                        r"\bcrack(ed|s)?\b", r"\bsinking\b", r"\bsubsid",
                        r"\bfootpath\b", r"\btile.*(broken|upturned)\b",
                        r"\bcrater\b", r"\bcollaps"]),
    ("Heritage Damage",[r"\bheritage\b", r"\bmonument\b", r"\bhistoric\b"]),
    ("Heat Hazard",    [r"\bheat\b", r"\bheatwave\b", r"\bsunstroke\b",
                        r"\b\d+\s*°\s*c\b", r"\bmelting\b", r"\btemperatures?\b",
                        r"\bburns?\b"]),
]

# ---------------------------------------------------------------------------
# LLM System Prompt (derived from agents.md enforcement rules)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a civic complaint classification agent. Your job is to classify citizen complaints.

For each complaint, return a JSON object with exactly these fields:
- "category": one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
- "priority": one of [Urgent, Standard, Low]
- "reason": one sentence citing specific words from the complaint description
- "flag": "NEEDS_REVIEW" if the category is genuinely ambiguous, otherwise ""

RULES:
1. Category must be EXACTLY one of the allowed values. No variations, synonyms, or sub-categories.
2. Priority must be "Urgent" if the description contains any of these severity keywords (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise "Standard" for moderate impact, "Low" for minor issues.
3. The reason must cite specific words from the description to justify the classification.
4. If the complaint does not clearly map to a single category, set category to "Other" and flag to "NEEDS_REVIEW".

Return ONLY valid JSON. No markdown, no explanation outside the JSON."""

# ---------------------------------------------------------------------------
# LLM client initialization (Groq preferred, Gemini as secondary)
# ---------------------------------------------------------------------------

def _get_llm_client():
    """
    Try to initialize an LLM client. Priority: Groq > Gemini.
    Returns (client, provider_name) or (None, None).
    """
    # Try Groq first (free, reliable, fast)
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            client = Groq(api_key=api_key)
            return client, "groq"
    except ImportError:
        pass

    # Try Gemini as secondary
    try:
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            client = genai.Client(api_key=api_key)
            return client, "gemini"
    except ImportError:
        pass

    return None, None


# ---------------------------------------------------------------------------
# LLM-based classification
# ---------------------------------------------------------------------------

GROQ_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
GEMINI_MODELS = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]


def _call_groq(client, prompt):
    """Call Groq API and return response text."""
    for model_name in GROQ_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                continue
            if "404" in error_str or "not_found" in error_str.lower():
                continue
            return None
    return None


def _call_gemini(client, prompt):
    """Call Gemini API and return response text."""
    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                config={"system_instruction": SYSTEM_PROMPT},
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                continue
            if "404" in error_str or "NOT_FOUND" in error_str:
                continue
            return None
    return None


def classify_complaint_llm(row: dict, client, provider: str) -> dict:
    """
    Classify a complaint using LLM (Groq or Gemini).
    Returns classified dict or None if LLM call fails.
    """
    description = row.get("description", "")
    complaint_id = row.get("complaint_id", "")

    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    prompt = f"Classify this citizen complaint:\n\"{description}\""

    # Call the appropriate provider
    if provider == "groq":
        text = _call_groq(client, prompt)
    else:
        text = _call_gemini(client, prompt)

    if not text:
        return None

    try:
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        result = json.loads(text)

        # Validate category
        if result.get("category") not in ALLOWED_CATEGORIES:
            result["category"] = "Other"
            result["flag"] = "NEEDS_REVIEW"

        # Validate priority
        if result.get("priority") not in ["Urgent", "Standard", "Low"]:
            result["priority"] = "Low"

        # Ensure flag field exists
        if "flag" not in result:
            result["flag"] = ""

        result["complaint_id"] = complaint_id
        return result

    except (json.JSONDecodeError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Regex-based classification (fallback)
# ---------------------------------------------------------------------------

def classify_complaint_regex(row: dict) -> dict:
    """
    Classify a single complaint using regex rules.
    Fallback when LLM is unavailable.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Determine category ---
    matched_categories = []
    matched_evidence = []

    for cat, patterns in CATEGORY_RULES:
        for pattern in patterns:
            match = re.search(pattern, desc_lower)
            if match:
                matched_categories.append(cat)
                matched_evidence.append(match.group())
                break

    if len(matched_categories) == 1:
        category = matched_categories[0]
        evidence_word = matched_evidence[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        evidence_word = matched_evidence[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        evidence_word = ""
        flag = "NEEDS_REVIEW"

    # --- Determine priority ---
    found_severity = [kw for kw in SEVERITY_KEYWORDS if re.search(r"\b" + kw, desc_lower)]

    if found_severity:
        priority = "Urgent"
    elif any(term in desc_lower for term in ["risk", "danger", "serious", "stranded", "dark"]):
        priority = "Standard"
    else:
        priority = "Low"

    # --- Build reason ---
    if found_severity and evidence_word:
        reason = (
            f"Description mentions '{evidence_word}' indicating {category}, "
            f"and severity keyword '{found_severity[0]}' triggers Urgent priority."
        )
    elif found_severity:
        reason = (
            f"Severity keyword '{found_severity[0]}' found in description triggers Urgent priority; "
            f"category set to {category}."
        )
    elif evidence_word:
        reason = f"Description mentions '{evidence_word}' indicating {category}."
    else:
        reason = "No clear category keywords found in description; classified as Other."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Unified classify function (LLM-first, regex fallback)
# ---------------------------------------------------------------------------

def classify_complaint(row: dict, client=None, provider=None) -> dict:
    """
    Classify a complaint. Uses LLM if available, falls back to regex.
    """
    if client and provider:
        result = classify_complaint_llm(row, client, provider)
        if result:
            return result
        print(f"  LLM failed for {row.get('complaint_id', '?')}, using regex fallback.")

    return classify_complaint_regex(row)


# ---------------------------------------------------------------------------
# Batch classification
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Uses LLM as primary classifier; falls back to regex if unavailable.
    """
    # Try to initialize LLM
    client, provider = _get_llm_client()
    if client:
        print(f"Using {provider.upper()} (LLM) as primary classifier.")
    else:
        print("No LLM available. Using regex fallback.")
        print("Tip: set GROQ_API_KEY (or GEMINI_API_KEY) and install groq (or google-genai).")

    results = []
    failed_rows = []
    llm_failures = 0

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                # If LLM failed 2+ times in a row, disable it for remaining rows
                if client and llm_failures >= 2:
                    print("  LLM quota exhausted. Switching to regex for remaining rows.")
                    client = None

                result = classify_complaint(row, client=client, provider=provider)
                out_row = dict(row)
                out_row["category"] = result["category"]
                out_row["priority"] = result["priority"]
                out_row["reason"] = result["reason"]
                out_row["flag"] = result["flag"]
                results.append(out_row)

            except Exception as e:
                print(f"Warning: row {i} failed classification ({e}), applying fallback.")
                out_row = dict(row)
                out_row["category"] = "Other"
                out_row["priority"] = "Low"
                out_row["reason"] = "Classification failed for this row."
                out_row["flag"] = "NEEDS_REVIEW"
                results.append(out_row)
                failed_rows.append(i)

    if not results:
        print("No rows to write.")
        return

    fieldnames = list(results[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows ({len(failed_rows)} failed to regex fallback).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
