import json
import os

def classify_complaint(description):
    """
    Core Logic: Categorizes civic issues and evaluates severity.
    Reflects the rules defined in agents.md and skills.md.
    """
    desc_lower = description.lower()
    
    # 1. Category Mapping (Skills)
    category_map = {
        "Water Supply": ["water", "leak", "pipe", "tanker", "no supply", "low pressure"],
        "Sewage & Sanitation": ["drain", "sewage", "gutter", "overflow", "stink", "manhole"],
        "Road Infrastructure": ["pothole", "crack", "road", "pavement", "bridge", "divider"],
        "Street Lighting": ["dark", "street light", "lamp", "bulb", "electricity", "short circuit"],
        "Garbage Collection": ["trash", "garbage", "bin", "waste", "dump", "litter"],
        "Public Health": ["mosquito", "fever", "epidemic", "clinic", "stagnant water"]
    }

    selected_category = "Unclassified"
    found_keywords = []

    for cat, keywords in category_map.items():
        for word in keywords:
            if word in desc_lower:
                selected_category = cat
                found_keywords.append(word)
                break
    
    # 2. Severity Assessment (Safety Triggers from agents.md)
    # High Priority triggers: Physical danger, accidents, or critical access
    high_priority_triggers = ["injury", "accident", "exposed wire", "flooding", "hospital", "emergency", "danger"]
    
    severity = "Low"
    if any(trigger in desc_lower for trigger in high_priority_triggers):
        severity = "High"
    elif selected_category != "Unclassified":
        severity = "Medium"

    # 3. Refusal/Flagging logic
    flag = "NONE"
    if selected_category == "Unclassified":
        flag = "INSUFFICIENT_DATA"

    return {
        "category": selected_category,
        "severity": severity,
        "logic_reasoning": found_keywords if found_keywords else ["None found"],
        "flag": flag,
        "original_text": description[:50] + "..." # Truncated for the report
    }

if __name__ == "__main__":
    # Test dataset representing common civic issues
    sample_complaints = [
        "Massive pothole near the city hospital causing traffic accidents.",
        "The street lights are not working on 5th Avenue, it is very dark.",
        "There is a water leak from the main pipe in front of my house.",
        "Garbage hasn't been collected for 3 days and it smells terrible."
    ]

    results = []
    print("--- Starting Classification Production ---")

    for complaint in sample_complaints:
        result = classify_complaint(complaint)
        results.append(result)
        print(f"Processed: {result['category']} | Severity: {result['severity']}")

    # 4. AUTOMATIC OUTPUT FILE GENERATION
    output_file = "uc0a_output.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\n[SUCCESS] {len(results)} cases processed.")
    print(f"[FILE CREATED] Results saved to: {os.path.abspath(output_file)}")