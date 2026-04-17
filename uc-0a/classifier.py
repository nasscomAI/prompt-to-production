import csv
import argparse
import os
import re

# Lead District AI Magistrate Persona & Taxonomy
# Grounded in uc-0a/README.md and agents.md
TAXONOMY = {
    "Pothole": [r"pothole", r"crater", r"sinkhole", r"road surface"],
    "Flooding": [r"flood", r"waterlogging", r"inundation", r"overflow", r"knee-deep", r"rain"],
    "Streetlight": [r"streetlight", r"unlit", r"dark", r"street light", r"lamp", r"flickering"],
    "Waste": [r"waste", r"trash", r"garbage", r"bins", r"dumping", r"refuse", r"dead animal", r"overflowing"],
    "Noise": [r"noise", r"loud", r"music", r"audible", r"sound", r"midnight"],
    "Road Damage": [r"road damage", r"tarmac", r"paving", r"broken road", r"surface", r"divider", r"subsidence", r"cracked"],
    "Heritage Damage": [r"heritage", r"ancient", r"statue", r"monument", r"temple", r"gate", r"old city", r"zoo", r"step well", r"riverfront"],
    "Heat Hazard": [r"heat", r"hot", r"melting", r"44°c", r"45°c", r"52°c", r"temperature", r"temperatures", r"sun", r"burned", r"bubbling", r"heatwave"],
    "Drain Blockage": [r"drain", r"blockage", r"sewage", r"gutter", r"manhole"],
    "Other": []
}

URGENT_KEYWORDS = [r"injury", r"child", r"school", r"hospital", r"ambulance", r"fire", r"hazard", r"fell", r"collapse", r"risk", r"sparking"]

def classify_complaint(description):
    """
    Lead District AI Magistrate Classification Engine.
    Employs regex-based word boundary detection to prevent false positives (e.g., Sun vs Sunday).
    """
    description_lower = description.lower()
    
    # 1. Category Determination with Priority Mapping
    # Rule 2: Heat and Heritage mapping priority
    category_scores = {}
    matched_keywords = {}

    for cat, keywords in TAXONOMY.items():
        if cat == "Other": continue
        matches = []
        for k in keywords:
            # Use \b for word boundaries to avoid 'sun' in 'sunday'
            if re.search(rf"\b{k}\b", description_lower):
                matches.append(k)
        if matches:
            category_scores[cat] = len(matches)
            matched_keywords[cat] = matches

    # Semantic Priority: Heat > Heritage > Others (based on count)
    assigned_category = "Other"
    found_keywords = []

    if "Heat Hazard" in category_scores:
        assigned_category = "Heat Hazard"
        found_keywords = matched_keywords["Heat Hazard"]
    elif "Heritage Damage" in category_scores:
        assigned_category = "Heritage Damage"
        found_keywords = matched_keywords["Heritage Damage"]
    elif category_scores:
        # Pick the one with highest keyword density
        assigned_category = max(category_scores, key=category_scores.get)
        found_keywords = matched_keywords[assigned_category]

    # 2. Priority Determination (Rule 3)
    priority = "Standard"
    trigger_word = ""
    for k in URGENT_KEYWORDS:
        if re.search(rf"\b{k}\b", description_lower):
            priority = "Urgent"
            trigger_word = k
            break
    
    # 3. Reasoning Generation (Persona: Lead District AI Magistrate)
    # Rule 4: Must cite specific words
    if assigned_category == "Other":
        reason = "Vague description; no recognized municipal category keywords found in text."
    else:
        reason = f"Classified as {assigned_category} based on detection of '{found_keywords[0]}'."
        if priority == "Urgent":
            reason += f" Urgent priority state-actioned due to high-risk trigger '{trigger_word}'."

    # 4. Ambiguity Flagging (Rule 5)
    flag = ""
    if assigned_category == "Other" or len(category_scores) > 1:
        flag = "NEEDS_REVIEW"

    return assigned_category, priority, reason, flag

def batch_classify(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Path {input_path} does not exist.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        # Ensure description column exists
        if 'description' not in reader.fieldnames:
            print(f"Error: 'description' column missing in {input_path}")
            return
            
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        
        for row in reader:
            cat, prio, reason, flag = classify_complaint(row['description'])
            row['category'] = cat
            row['priority'] = prio
            row['reason'] = reason
            row['flag'] = flag
            results.append(row)

    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Magistrate Audit Complete: {len(results)} records processed -> {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Urban Governance Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
