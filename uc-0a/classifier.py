"""
UC-0A — Complaint Classifier
Implementation dynamically bound to agents.md (RICE) and skills.md specs.
"""
import argparse
import csv
import re
import os

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

# Stems and word variations for mandatory severity triggers
SEVERITY_PATTERNS = [
    (r"\binjur(y|ies|ed)?\b", "injury"),
    (r"\bchild(ren)?\b", "child"),
    (r"\bschools?\b", "school"),
    (r"\bhospitals?|hospitalised|hospitalized\b", "hospital"),
    (r"\bambulances?\b", "ambulance"),
    (r"\bfires?\b", "fire"),
    (r"\bhazards?|hazardous\b", "hazard"),
    (r"\bfell|fall|falling\b", "fell"),
    (r"\bcollaps(e|ed|ing)?\b", "collapse"),
]

# Category matching patterns based on domain keywords
CATEGORY_PATTERNS = [
    ("Pothole", r"\b(pothole|potholes|crater)\b"),
    ("Heritage Damage", r"\b(heritage|historic|monument)\b"),
    ("Heat Hazard", r"\b(heatwave|heat hazard|extreme heat)\b"),
    ("Drain Blockage", r"\b(drain|drains|sewer|gutters?|manhole|choked drain|drainage)\b"),
    ("Flooding", r"\b(flood|flooded|flooding|floods|waterlog|waterlogging|underpass|rainwater|water standing)\b"),
    ("Streetlight", r"\b(streetlight|streetlights|light out|lights out|sparking|dark at night)\b"),
    ("Waste", r"\b(garbage|waste|trash|bins?|dumped|dead animal|refuse)\b"),
    ("Noise", r"\b(noise|loud speaker|drilling|music|mid-night|weeknights|sound|engines on)\b"),
    ("Road Damage", r"\b(road surface|cracked|sinking|footpath|tiles broken|upturned|pavement|road collapsed)\b"),
]


def load_agent_spec(agents_path: str = "agents.md") -> str:
    """Load RICE agent specification from agents.md if present."""
    if os.path.exists(agents_path):
        with open(agents_path, mode="r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_skills_spec(skills_path: str = "skills.md") -> str:
    """Load skills specification from skills.md if present."""
    if os.path.exists(skills_path):
        with open(skills_path, mode="r", encoding="utf-8") as f:
            return f.read()
    return ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row following RICE enforcement rules (agents.md)
    and skill specs (skills.md).
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint description is missing or blank.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()
    
    # 1. Category Classification (Enforcement Rule 1: Must be one of 10 allowed categories)
    matched_category = None
    for category_name, pattern in CATEGORY_PATTERNS:
        if re.search(pattern, desc_lower):
            matched_category = category_name
            break

    flag = ""
    if matched_category:
        category = matched_category
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Priority Determination (Enforcement Rule 2: Urgent if severity keywords present)
    matched_severity_triggers = []
    for pattern, canonical_word in SEVERITY_PATTERNS:
        match = re.search(pattern, desc_lower)
        if match:
            matched_severity_triggers.append(match.group(0))

    if matched_severity_triggers:
        priority = "Urgent"
    elif category in ["Noise"]:
        priority = "Low"
    else:
        priority = "Standard"

    # 3. Reason Generation (Enforcement Rule 3: Single-sentence reason citing description words)
    short_snippet = description if len(description) <= 60 else description[:57] + "..."
    if matched_severity_triggers:
        triggers_str = ", ".join(f"'{t}'" for t in matched_severity_triggers)
        reason = f"Classified as {category} with Urgent priority because complaint mentions {triggers_str}."
    else:
        reason = f"Classified as {category} with {priority} priority based on report: '{short_snippet}'."

    # 4. Refusal/Flag condition (Enforcement Rule 4: NEEDS_REVIEW for ambiguous/Other)
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }



def batch_classify(input_path: str, output_path: str, agents_path: str = "agents.md", skills_path: str = "skills.md"):
    """
    Read input CSV, classify each row according to skills.md specification, and write results CSV.
    """
    # Load specs to ensure alignment
    agents_spec = load_agent_spec(agents_path)
    skills_spec = load_skills_spec(skills_path)
    if agents_spec:
        print(f"[Info] Loaded RICE spec from {agents_path}")
    if skills_spec:
        print(f"[Info] Loaded Skills spec from {skills_path}")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    results = []
    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    flagged_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"Successfully processed {len(results)} rows ({flagged_count} flagged for review). Results saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    parser.add_argument("--agents", default="agents.md", help="Path to agents.md RICE spec")
    parser.add_argument("--skills", default="skills.md", help="Path to skills.md spec")
    args = parser.parse_args()
    batch_classify(args.input, args.output, agents_path=args.agents, skills_path=args.skills)
    print(f"Done. Results written to {args.output}")


