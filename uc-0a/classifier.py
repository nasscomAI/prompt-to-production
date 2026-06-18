import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    text = description.lower()
    
    # Define category patterns
    categories_patterns = {
        "Pothole": [r"\bpotholes?\b", r"\bcrater\b"],
        "Flooding": [r"\bfloods?\b", r"\bflooded\b", r"\bflooding\b", r"\brainwater\b", r"\bwaterlogging\b"],
        "Streetlight": [r"\bstreetlights?\b", r"\blamps?\b", r"\bdark(ness)?\b", r"\blight(?!s?\s+rain)\b"],
        "Waste": [r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\bdebris\b"],
        "Noise": [r"\bnoise\b", r"\bdrilling\b", r"\bloud\b", r"\bidling\b"],
        "Road Damage": [r"\broad\s+collapsed\b", r"\broad\s+damage\b", r"\broad\s+collapse\b", r"\broad\s+collapses\b"],
        "Heritage Damage": [r"\bheritage\b", r"\bmonument\b"],
        "Heat Hazard": [r"\bheat\b", r"\btemperature\b", r"\bhot\b"],
        "Drain Blockage": [r"\bdrains?\b", r"\bsewage\b", r"\bgutter\s+blocked\b", r"\bgutters?\b"]
    }
    
    categories_found = []
    citations_categories = []
    
    for category_name, patterns in categories_patterns.items():
        matched_words = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # capture the actual matched string
                matched_words.extend(matches)
        if matched_words:
            categories_found.append(category_name)
            citations_categories.extend(matched_words)
            
    # De-duplicate categories while preserving order
    unique_categories = []
    for cat in categories_found:
        if cat not in unique_categories:
            unique_categories.append(cat)
            
    flag = ""
    if len(unique_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(unique_categories) > 1:
        category = unique_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        category = unique_categories[0]
        
    # Priority check
    urgent_patterns = [
        r"\binjur(y|ies|ed)\b",
        r"\bchild(ren)?\b",
        r"\bschools?\b",
        r"\bhospital(ised|ized|s)?\b",
        r"\bambulances?\b",
        r"\bfires?\b",
        r"\bhazards?\b",
        r"\bfell\b",
        r"\bcollapse(d|s)?\b"
    ]
    
    matched_urgent = []
    for pattern in urgent_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # If the regex has a group like injur(y|ies|ed), matches will be a list of tuples or group strings.
            # We want the full matched string, so let's find the match object.
            for match_obj in re.finditer(pattern, text):
                matched_urgent.append(match_obj.group(0))
                
    if matched_urgent:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    # Reason construction
    all_citations = list(sorted(set(citations_categories + matched_urgent)))
    if all_citations:
        citations_str = ", ".join(f"'{c}'" for c in all_citations)
        reason = f"Classified as {category} with {priority} priority citing {citations_str} from the description."
    else:
        reason = f"Classified as {category} with {priority} priority based on context."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                row.update(result)
            except Exception as e:
                row.update({
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
            writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
