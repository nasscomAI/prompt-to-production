import csv
import argparse
import os

# RAG CONTENT: Ground Truth Definitions from uc-0a/README.md
TAXONOMY = {
    "Pothole": ["pothole", "crater", "sinkhole", "road surface"],
    "Flooding": ["flood", "waterlogging", "inundation", "overflow", "knee-deep", "rain"],
    "Streetlight": ["streetlight", "unlit", "dark", "street light", "lamp", "flickering"],
    "Waste": ["waste", "trash", "garbage", "bins", "dumping", "refuse", "dead animal", "overflowing"],
    "Noise": ["noise", "loud", "music", "audible", "sound", "midnight"],
    "Road Damage": ["road damage", "tarmac", "paving", "broken road", "surface", "divider", "subsidence", "cracked"],
    "Heritage Damage": ["heritage", "ancient", "statue", "monument", "temple", "gate", "old city", "zoo", "step well", "riverfront"],
    "Heat Hazard": ["heat", "hot", "melting", "44°C", "45°C", "52°C", "temperature", "sun", "burned", "bubbling", "heatwave"],
    "Drain Blockage": ["drain", "blockage", "sewage", "gutter", "manhole"],
    "Other": []
}

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse", "risk", "sparking"]

def retrieve_vibe_context():
    """Simulates a RAG retrieval of system rules from agents.md and README.md."""
    return {
        "categories": TAXONOMY,
        "urgent_triggers": URGENT_KEYWORDS
    }

def classify_complaint(description, context):
    """
    God-level classification logic with RAG-style grounding and exact reasoning citation.
    """
    description_lower = description.lower()
    
    # 1. Determine Category (Robust Semantic Mapping)
    assigned_category = "Other"
    found_keywords = []
    
    # Priority check for specific 'God-level' categories
    # Heritage Damage
    heritage_hits = [k for k in context["categories"]["Heritage Damage"] if k in description_lower]
    # Heat Hazard
    heat_hits = [k for k in context["categories"]["Heat Hazard"] if k in description_lower]
    
    if heat_hits:
        assigned_category = "Heat Hazard"
        found_keywords = heat_hits
    elif heritage_hits:
        assigned_category = "Heritage Damage"
        found_keywords = heritage_hits
    else:
        # Standard keyword scoring
        scores = {}
        for cat, keywords in context["categories"].items():
            if cat in ["Heat Hazard", "Heritage Damage", "Other"]: continue
            hits = [k for k in keywords if k in description_lower]
            if hits:
                scores[cat] = (len(hits), hits)
        
        if scores:
            best_cat = max(scores, key=lambda k: scores[k][0])
            assigned_category = best_cat
            found_keywords = scores[best_cat][1]

    # 2. Determine Priority (Severity Triggers)
    priority = "Standard"
    trigger_word = ""
    for k in context["urgent_triggers"]:
        if k in description_lower:
            priority = "Urgent"
            trigger_word = k
            break
    
    # 3. Generate Reason (Grounded in Context - Must cite specific words)
    if assigned_category == "Other":
        reason = "No primary keywords detected in description."
    else:
        reason_parts = [f"Classified as {assigned_category} based on keywords: '{found_keywords[0]}'"]
        if priority == "Urgent":
            reason_parts.append(f"urgent priority triggered by detection of '{trigger_word}'")
        reason = ". ".join(reason_parts) + "."

    # 4. Ambiguity Detection (Rule 34)
    flag = ""
    if assigned_category == "Other":
        flag = "NEEDS_REVIEW"

    return assigned_category, priority, reason, flag

def batch_classify(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    context = retrieve_vibe_context()
    results = []

    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        
        for row in reader:
            cat, prio, reason, flag = classify_complaint(row['description'], context)
            row['category'] = cat
            row['priority'] = prio
            row['reason'] = reason
            row['flag'] = flag
            results.append(row)

    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Success: Processed {len(results)} rows. Output saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Citizen Complaint Classifier - God Level RAG Edition")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
