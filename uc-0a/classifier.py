import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules in agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Category Classification Logic (Exact strings from taxonomy)
    category = "Other"
    
    # Define keywords for categories
    category_map = {
        "Pothole": [r"pothole", r"crater", r"sinkhole"],
        "Heritage Damage": [r"heritage", r"ancient", r"monument", r"step\s*well", r"historic"],
        "Heat Hazard": [r"heat", r"melting", r"bubbling", r"surface\s*temperature", r"°c", r"44°c", r"45°c", r"52°c", r"\bsun\b", r"burns"],
        "Waste": [r"waste", r"garbage", r"bins", r"litter", r"cleared"],
        "Noise": [r"noise", r"loud", r"music", r"audible", r"2am"],
        "Streetlight": [r"streetlight", r"unlit", r"dark", r"lighting", r"wiring\s*theft"],
        "Flooding": [r"flood", r"waterlogging", r"submerged", r"inundated"],
        "Drain Blockage": [r"drain", r"sewage", r"drainage", r"clogged"],
        "Road Damage": [r"road", r"tarmac", r"paving", r"surface", r"divider", r"bus\s*shelter", r"bench"]
    }

    found_cat_word = None
    for cat, kws in category_map.items():
        for kw in kws:
            if re.search(kw, description, re.IGNORECASE):
                category = cat
                found_cat_word = kw
                break
        if found_cat_word:
            break

    # 2. Priority Classification Logic
    # Urgent if description contains specific keywords
    urgent_keywords = [r"injury", r"child", r"school", r"hospital", r"ambulance", r"fire", r"hazard", r"fell", r"collapse", r"injured", r"dangerous", r"unsafe", r"risk"]
    priority = "Standard"
    
    found_urgent = []
    for kw in urgent_keywords:
        if re.search(kw, description, re.IGNORECASE):
            found_urgent.append(kw)
    
    if found_urgent:
        priority = "Urgent"
    elif re.search(r"minor|low\s*priority|not\s*urgent", description, re.IGNORECASE):
        priority = "Low"
    
    # 3. Reason Field (Strictly one sentence, citing specific words)
    # We find a representative keyword to cite
    char_word = "general description"
    if found_urgent:
        char_word = found_urgent[0]
    elif found_cat_word:
        char_word = found_cat_word
    
    # Clean up char_word if it's a regex
    characteristic_word = str(char_word).replace(r"\b", "").replace(r"\s*", " ")
            
    reason = f"The complaint is classified as {category} with {priority} priority because the description mentions '{characteristic_word}'."

    # 4. Refusal / Flagging Condition
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
        "description": row.get("description", "")
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint per row, write output CSV.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Basic validation for empty rows
                if not any(row.values()):
                    continue
                results.append(classify_complaint(row))
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    if not results:
        print("No data processed.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag", "description"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results_[city].csv")
    args = parser.parse_args()
    
    print(f"Processing {args.input}...")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
