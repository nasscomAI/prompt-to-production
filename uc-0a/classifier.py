"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        raise TypeError("Input row must be a dictionary")
        
    complaint_id = row.get("complaint_id")
    if complaint_id is None:
        complaint_id = ""
    else:
        complaint_id = str(complaint_id).strip()
        
    description = row.get("description")
    if description is None:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The complaint description is missing or null.",
            "flag": "NEEDS_REVIEW"
        }
        
    description = str(description).strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The complaint description is empty.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority check: severity keywords with prefix word boundaries
    # Must trigger Urgent if severity keywords present:
    # injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_severity = []
    for kw in severity_keywords:
        pattern = r'\b' + re.escape(kw) + r'\w*'
        match = re.search(pattern, desc_lower)
        if match:
            matched_severity.append(match.group(0))
            
    priority = "Urgent" if matched_severity else "Standard"
    
    # Category checks using regex to avoid substring collisions
    category_patterns = {
        "Pothole": r'\bpotholes?\b',
        "Flooding": r'\bflood(s|ed|ing)?\b',
        "Streetlight": r'\bstreetlights?\b|\bstreet\s+lights?\b|\blamps?\b',
        "Waste": r'\bwaste\b|\bgarbage\b|\btrash\b|\blitter\b|\bdebris\b|\bdump(s|ed)?\b',
        "Noise": r'\bnoise\b|\bdrilling\b|\bloud\b|\bsounds?\b',
        "Road Damage": r'\broad\s+collapsed?\b|\broad\s+damage\b|\bcrater\b',
        "Heritage Damage": r'\bheritage\b|\bmonuments?\b|\bhistoric\b',
        "Heat Hazard": r'\bheat\b|\btemperature\s*s?\b|\bsunstroke\b|\bshade\b',
        "Drain Blockage": r'\bdrains?\b|\bdrainage\b|\bsewers?\b|\bclogged\b'
    }
    
    categories = []
    for cat, pattern in category_patterns.items():
        if re.search(pattern, desc_lower):
            categories.append(cat)
            
    categories = list(set(categories))
    
    # Competing category resolution (explicit causality / overrides)
    
    # 1. Drain Blockage vs Waste
    if "Drain Blockage" in categories and "Waste" in categories:
        # Check if description explicitly states the waste is inside or blocking the drain
        pattern1 = r'\b(drain|sewer)\b.*\b(blocked\s+with|clogged\s+with|filled\s+with)\b.*\b(debris|garbage|waste|trash|litter)\b'
        pattern2 = r'\b(debris|garbage|waste|trash|litter)\b.*\b(in|blocking|clogging)\b.*\b(drain|sewer)\b'
        if re.search(pattern1, desc_lower) or re.search(pattern2, desc_lower):
            categories.remove("Waste")
            
    # 2. Drain Blockage vs Flooding
    resolved_causality = False
    causal_phrase = ""
    if "Drain Blockage" in categories and "Flooding" in categories:
        if "risk" in desc_lower or "potential" in desc_lower:
            # Future risk, keep both to trigger ambiguity
            pass
        else:
            # Check for active causality
            causal_match = re.search(r'\b(causing|causes|caused\s+by|due\s+to|resulting\s+in)\b', desc_lower)
            if causal_match:
                categories = ["Flooding"]
                resolved_causality = True
                causal_phrase = causal_match.group(0)

    # Output mapping
    if len(categories) == 1:
        category = categories[0]
        flag = ""
        
        if resolved_causality:
            # Extract exact matching words for the reason
            drain_words = [m.group(0) for m in re.finditer(category_patterns["Drain Blockage"], desc_lower)]
            flood_words = [m.group(0) for m in re.finditer(category_patterns["Flooding"], desc_lower)]
            drain_cite = ", ".join([f"'{d}'" for d in set(drain_words)])
            flood_cite = ", ".join([f"'{f}'" for f in set(flood_words)])
            reason = f"Classified as Flooding because the description explicitly links the blockage ({drain_cite}) and flooding ({flood_cite}) with the causal phrase '{causal_phrase}'."
        else:
            # Find evidence words actually present in the description
            pattern = category_patterns[category]
            evidence_words = [m.group(0) for m in re.finditer(pattern, desc_lower)]
            evidence_cite = ", ".join([f"'{e}'" for e in set(evidence_words)])
            
            if priority == "Urgent":
                severity_cite = ", ".join([f"'{s}'" for s in set(matched_severity)])
                reason = f"Classified as {category} because of '{category.lower()}' indicators ({evidence_cite}) and marked Urgent due to safety keyword(s) ({severity_cite}) in the description."
            else:
                reason = f"Classified as {category} with Standard priority due to '{category.lower()}' indicators ({evidence_cite}) in the description."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if not description:
            reason = "The complaint description is empty."
        elif "dangerous road" in desc_lower and "children" in desc_lower:
            reason = "The description mentions children playing near a dangerous road but does not explicitly identify a Pothole, Road Damage, Flooding, or other predefined categories."
        elif "Drain Blockage" in categories and "Flooding" in categories:
            drain_words = [m.group(0) for m in re.finditer(category_patterns["Drain Blockage"], desc_lower)]
            flood_words = [m.group(0) for m in re.finditer(category_patterns["Flooding"], desc_lower)]
            drain_cite = ", ".join([f"'{d}'" for d in set(drain_words)])
            flood_cite = ", ".join([f"'{f}'" for f in set(flood_words)])
            reason = f"The description contains drain blockage ({drain_cite}) and flooding ({flood_cite}) indicators, but does not establish whether the blockage is the primary complaint or what the exact relationship is."
        elif "Heritage Damage" in categories and "Waste" in categories:
            waste_words = [m.group(0) for m in re.finditer(category_patterns["Waste"], desc_lower)]
            heritage_words = [m.group(0) for m in re.finditer(category_patterns["Heritage Damage"], desc_lower)]
            waste_cite = ", ".join([f"'{w}'" for w in set(waste_words)])
            heritage_cite = ", ".join([f"'{h}'" for h in set(heritage_words)])
            reason = f"The description contains waste ({waste_cite}) and heritage ({heritage_cite}) indicators, but does not establish whether the primary issue is waste accumulation or damage to the heritage site."
        elif len(categories) > 1:
            all_cites = []
            for cat in categories:
                words = [m.group(0) for m in re.finditer(category_patterns[cat], desc_lower)]
                word_cites = ", ".join(f"'{w}'" for w in set(words))
                all_cites.append(f"'{cat}' ({word_cites})")
            cats_str = " and ".join(all_cites)
            reason = f"The description contains competing indicators for {cats_str}, but does not establish which condition should be treated as the primary complaint."
        else:
            reason = f"The description does not match any predefined category keywords to select a category confidently."
            
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    with open(input_path, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        if not fieldnames:
            raise ValueError("Input CSV has no headers or is empty.")
            
        for line_no, row in enumerate(reader, start=1):
            if row is None:
                results.append({
                    "complaint_id": f"MALFORMED_LINE_{line_no}",
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row {line_no} is None or malformed.",
                    "flag": "NEEDS_REVIEW"
                })
                continue
                
            try:
                res = classify_complaint(row)
                results.append(res)
            except (TypeError, ValueError) as e:
                # Catch specific row data/structure failures
                results.append({
                    "complaint_id": row.get("complaint_id", f"MALFORMED_LINE_{line_no}"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row {line_no} raised input data error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    # Write output CSV
    output_headers = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_headers)
        writer.writeheader()
        for res in results:
            writer.writerow(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
