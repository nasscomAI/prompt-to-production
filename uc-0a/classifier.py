"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import json
import urllib.request

ALLOWED_CATEGORIES = {
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise',
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
}
SEVERITY_KEYWORDS = [
    'injury', 'child', 'school', 'hospital', 'ambulance',
    'fire', 'hazard', 'fell', 'collapse'
]
ALLOWED_PRIORITIES = {'Urgent', 'Standard', 'Low'}

def generate_llm_classification(row: dict) -> dict:
    """Gets raw classification from LLM (or deterministic mock if no API key)."""
    desc = row.get("description", "")
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        # Phase 2 Deterministic test mock
        # Intentionally returns some bad labels (like "Water Logging") to test deterministic recovery.
        desc_lower = desc.lower()
        if "pothole" in desc_lower and "school" in desc_lower: return {"category": "Road Maintenance", "priority": "Standard", "reason": ""}
        if "pothole" in desc_lower: return {"category": "Pothole", "priority": "Medium", "reason": "Pothole reported."}
        if "flooded" in desc_lower and "drain" in desc_lower: return {"category": "Water Logging", "priority": "High", "reason": ""}
        if "flooded" in desc_lower or "floods" in desc_lower: return {"category": "Water Logging", "priority": "High", "reason": ""}
        if "streetlights" in desc_lower or "lights out" in desc_lower: return {"category": "Lighting", "priority": "Low", "reason": ""}
        if "hazard" in desc_lower: return {"category": "Streetlight", "priority": "Medium", "reason": ""}
        if "garbage" in desc_lower or "waste" in desc_lower: return {"category": "Waste", "priority": "Low", "reason": ""}
        if "music" in desc_lower: return {"category": "Noise Pollution", "priority": "Low", "reason": ""}
        if "cracked" in desc_lower: return {"category": "Road Damage", "priority": "Medium", "reason": ""}
        if "manhole" in desc_lower: return {"category": "Missing Cover", "priority": "High", "reason": ""}
        if "animal" in desc_lower: return {"category": "Animal Control", "priority": "Low", "reason": "Dead animal found"}
        if "heritage" in desc_lower: return {"category": "Heritage", "priority": "Medium", "reason": ""}
        if "footpath" in desc_lower: return {"category": "Footpath Damage", "priority": "High", "reason": ""}
        return {"category": "Unknown", "priority": "Low", "reason": ""}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = (
        "Classify this citizen complaint by category and priority.\n"
        f"Description: {desc}\n\n"
        "Output ONLY a JSON object with keys: category, priority, reason, flag."
    )

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
    except Exception as e:
        return {"category": "Other", "priority": "Standard", "reason": str(e), "flag": "ERROR"}

def recover_category(desc_lower: str) -> str:
    """Deterministically recover category from evidence in the description."""
    if "pothole" in desc_lower: return "Pothole"
    if "flood" in desc_lower or "water logging" in desc_lower: return "Flooding"
    if "streetlight" in desc_lower or "light" in desc_lower: return "Streetlight"
    if "waste" in desc_lower or "garbage" in desc_lower or "bin" in desc_lower: return "Waste"
    if "noise" in desc_lower or "music" in desc_lower: return "Noise"
    if "road damage" in desc_lower or "broken road" in desc_lower or "cracked" in desc_lower or "manhole" in desc_lower or "footpath" in desc_lower: return "Road Damage"
    if "heritage" in desc_lower: return "Heritage Damage"
    if "heat" in desc_lower: return "Heat Hazard"
    if "drain blockage" in desc_lower or "blocked" in desc_lower or "drain" in desc_lower: return "Drain Blockage"
    return "Other"

def classify_complaint(row: dict) -> dict:
    raw_result = generate_llm_classification(row)

    category = raw_result.get("category", "Other")
    priority = raw_result.get("priority", "Standard")
    reason = raw_result.get("reason", "")
    flag = raw_result.get("flag", "")

    desc = row.get("description", "")
    desc_lower = desc.lower()

    # 1. Deterministic Category Validation & Recovery
    if category not in ALLOWED_CATEGORIES:
        recovered = recover_category(desc_lower)
        category = recovered
        if recovered == "Other":
            flag = "NEEDS_REVIEW"

    # 2. Deterministic Priority Validation
    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    # 3. Deterministic Severity Keyword Rule (Independent of ambiguity)
    for keyword in SEVERITY_KEYWORDS:
        if keyword in desc_lower:
            priority = "Urgent"
            break

    # 4. Reason Enforcement (Grounded fallback)
    if not reason or not reason.strip():
        snippet = desc[:50] + "..." if len(desc) > 50 else desc
        reason = f"Classified based on evidence in description: '{snippet}'"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    results = []
    for row in rows:
        results.append(classify_complaint(row))

    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


