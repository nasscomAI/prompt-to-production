import argparse
import csv
import logging
import os
import re
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ComplaintClassifier")

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
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

ALLOWED_FLAGS = ["NEEDS_REVIEW", ""]

def load_agents_config(config_path: str = "agents.md") -> dict:
    """Loads R.I.C.E configuration from agents.md file without hard PyYAML dependency."""
    if not os.path.exists(config_path):
        return {}
    
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback simple parser for agents.md YAML format
        config = {"role": "", "intent": "", "context": {}, "enforcement": []}
        current_section = None
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str or line_str.startswith("#"):
                    continue
                if line_str.startswith("role:"):
                    config["role"] = line_str.split("role:", 1)[1].strip().strip('"')
                elif line_str.startswith("intent:"):
                    config["intent"] = line_str.split("intent:", 1)[1].strip().strip('"')
                elif line_str.startswith("enforcement:"):
                    current_section = "enforcement"
                elif current_section == "enforcement" and line_str.startswith("-"):
                    rule = line_str[1:].strip().strip('"')
                    config["enforcement"].append(rule)
        return config

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    Classifies a single city complaint into a structured record enforcing taxonomy,
    priority triggers, reasoning, and review flags.

    Input: dict containing 'description' and 'location' (plus 'id' if available)
    Output: dict containing 'id', 'description', 'location', 'category', 'priority', 'reason', 'flag'
    """
    if not isinstance(row, dict):
        raise ValueError("Input row must be a dictionary.")

    id_val = str(row.get("id", "")).strip()
    description = str(row.get("description", "")).strip()
    location = str(row.get("location", "")).strip()
    desc_lower = description.lower()

    word_count = len(description.split())
    vague_phrases = [
        "something happened",
        "need general information",
        "weird",
        "not sure",
        "test",
        "information about",
    ]

    is_vague = word_count < 6 or any(phrase in desc_lower for phrase in vague_phrases)

    category = "Other"
    reason_words = ""

    if not is_vague:
        if "pothole" in desc_lower:
            category = "Pothole"
            reason_words = "pothole"
        elif "flood" in desc_lower or "waterlogging" in desc_lower:
            category = "Flooding"
            reason_words = "flooding"
        elif "streetlight" in desc_lower or "street light" in desc_lower or "dark at night" in desc_lower:
            category = "Streetlight"
            reason_words = "streetlight"
        elif "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "uncollected" in desc_lower:
            category = "Waste"
            reason_words = "waste accumulating" if "waste accumulating" in desc_lower else ("garbage" if "garbage" in desc_lower else "waste")
        elif "noise" in desc_lower or "loud" in desc_lower:
            category = "Noise"
            reason_words = "loud noise" if "loud noise" in desc_lower else ("noise" if "noise" in desc_lower else "loud")
        elif "heritage" in desc_lower or "shaniwar wada" in desc_lower or "historic" in desc_lower or "monument" in desc_lower:
            category = "Heritage Damage"
            reason_words = "historic structure masonry" if "historic" in desc_lower and "masonry" in desc_lower else ("historic" if "historic" in desc_lower else "heritage")
        elif "heat" in desc_lower or "fainting" in desc_lower or "sunstroke" in desc_lower:
            category = "Heat Hazard"
            reason_words = "heat hazard" if "heat hazard" in desc_lower else ("heat" if "heat" in desc_lower else "sunstroke")
        elif "drain" in desc_lower or "sewage" in desc_lower or "overflowing" in desc_lower:
            category = "Drain Blockage"
            reason_words = "drain blockage" if "drain blockage" in desc_lower else ("drain" if "drain" in desc_lower else "sewage")
        elif "road damage" in desc_lower or "pavement" in desc_lower or "street collapse" in desc_lower or "asphalt" in desc_lower:
            category = "Road Damage"
            reason_words = "road damage" if "road damage" in desc_lower else ("pavement" if "pavement" in desc_lower else "road")

    # Enforce allowed taxonomy list
    if category not in ALLOWED_CATEGORIES:
        logger.warning(f"Category '{category}' outside allowed taxonomy. Defaulting to 'Other'.")
        category = "Other"

    # Severity Keyword Enforcement (Word Boundary Regex Case-Insensitive)
    triggered_keywords = [kw for kw in SEVERITY_KEYWORDS if re.search(r"\b" + re.escape(kw) + r"\b", desc_lower)]

    if triggered_keywords:
        priority = "Urgent"
        kw_str = ", ".join(triggered_keywords)
        reason = f"Urgent priority assigned due to severity keywords '{kw_str}' in description: '{description}'."
    else:
        priority = "Low" if category in ["Other", "Streetlight"] else "Standard"
        if reason_words:
            reason = f"Classified as {category} based on specific description terms '{reason_words}'."
        else:
            reason = f"Description lacks specific diagnostic terms: '{description}'."

    # Ambiguity / Review Flag Enforcement
    if is_vague or category == "Other":
        category = "Other"
        flag = "NEEDS_REVIEW"
        if not triggered_keywords:
            reason = f"Ambiguous complaint description '{description}' requires manual review."
    else:
        flag = ""

    return {
        "id": id_val,
        "description": description,
        "location": location,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

def batch_classify(input_path: str, output_path: str) -> str:
    """
    Skill: batch_classify
    Reads CSV file, processes each valid complaint row with error handling,
    logs and skips malformed rows, and writes results CSV.
    """
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    skipped_rows = 0

    logger.info(f"Starting batch classification of {input_path}...")

    with open(input_path, "r", encoding="utf-8-sig") as f_in:
        reader = csv.DictReader(f_in)
        if reader.fieldnames is None or "description" not in reader.fieldnames:
            logger.error(f"Input file {input_path} missing required 'description' header.")
            raise ValueError(f"Input file {input_path} missing required 'description' header.")

        for line_num, row in enumerate(reader, start=2):
            try:
                if not row or not isinstance(row, dict):
                    logger.warning(f"Line {line_num}: Empty or invalid row format. Skipping.")
                    skipped_rows += 1
                    continue

                desc = row.get("description")
                if desc is None or not str(desc).strip():
                    logger.warning(f"Line {line_num}: Malformed row missing non-empty 'description': {row}. Skipping.")
                    skipped_rows += 1
                    continue

                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                logger.error(f"Line {line_num}: Error processing row {row}: {e}. Skipping row.")
                skipped_rows += 1
                continue

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = ["id", "description", "location", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    logger.info(f"Batch classification complete. {len(results)} rows processed, {skipped_rows} skipped.")
    logger.info(f"Results written to {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="UC-0A City Complaint Classifier")
    parser.add_argument("--input", default="../data/city-test-files/test_pune.csv", help="Input CSV path")
    parser.add_argument("--output", default="results_pune.csv", help="Output CSV path")
    args = parser.parse_args()

    # Load agents.md R.I.C.E config if present
    load_agents_config("agents.md")

    batch_classify(args.input, args.output)

if __name__ == "__main__":
    main()
