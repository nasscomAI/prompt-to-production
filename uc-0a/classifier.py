"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on agent constraints.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Identify priority based on severity keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            break

    # 2. Identify category using keyword matching
    found_kws = []
    
    if "pothole" in desc or "crater" in desc:
        found_kws.append("pothole")
    if "flood" in desc or "waterlogging" in desc:
        found_kws.append("flood")
    if "drain" in desc:
        found_kws.append("drain")
    if "streetlight" in desc or "lights out" in desc:
        found_kws.append("streetlight" if "streetlight" in desc else "lights out")
    if "garbage" in desc or "waste" in desc or "dead animal" in desc:
        found_kws.append("garbage" if "garbage" in desc else "waste" if "waste" in desc else "dead animal")
    if "music" in desc or "noise" in desc:
        found_kws.append("music" if "music" in desc else "noise")
    if "road surface" in desc or "footpath" in desc:
        found_kws.append("road surface" if "road surface" in desc else "footpath")
    if "heritage" in desc:
        found_kws.append("heritage")
        
    category = "Other"
    flag = ""
    reason = ""
    
    # 3. Handle specific matched cases and intentional ambiguity
    if len(found_kws) > 1:
        if "flood" in found_kws and "drain" in found_kws:
            category = "Flooding"
            reason = "The description explicitly mentions 'flood' alongside 'drain'."
        elif "heritage" in found_kws and "lights out" in found_kws:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason = "Mentions both 'heritage' and 'lights out', making it genuinely ambiguous."
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason = f"Multiple conflicting issues detected ({', '.join(found_kws)}), requiring review."
    elif len(found_kws) == 1:
        # Map keyword back to category
        kw = found_kws[0]
        if kw in ["pothole"]: category = "Pothole"
        elif kw in ["flood"]: category = "Flooding"
        elif kw in ["drain"]: category = "Drain Blockage"
        elif kw in ["streetlight", "lights out"]: category = "Streetlight"
        elif kw in ["garbage", "waste", "dead animal"]: category = "Waste"
        elif kw in ["music", "noise"]: category = "Noise"
        elif kw in ["road surface", "footpath"]: category = "Road Damage"
        elif kw in ["heritage"]: category = "Heritage Damage"
        
        reason = f"The description uniquely cites '{kw}', which dictates this categorization."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No familiar taxonomy keywords were found, leaving it ambiguous."

    # Edge cases specified explicitly for this triage logic
    if "manhole cover missing" in desc:
        category = "Road Damage"
        reason = "The description cites 'manhole cover missing', categorized directly as Road Damage."

    out = row.copy()
    out["category"] = category
    out["priority"] = priority
    out["reason"] = reason
    out["flag"] = flag
    return out


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                print("Input CSV is empty.")
                return
            fieldnames = reader.fieldnames
            if "category" not in fieldnames:
                fieldnames.extend(["category", "priority", "reason", "flag"])
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return
        
    results = []
    for row in rows:
        try:
            if not row.get("description"):
                row_out = row.copy()
                row_out["category"] = "Other"
                row_out["priority"] = "Low"
                row_out["reason"] = "Null description provided."
                row_out["flag"] = "NEEDS_REVIEW"
                results.append(row_out)
                continue
                
            res = classify_complaint(row)
            results.append(res)
        except Exception as e:
            print(f"Error classifying row {row.get('complaint_id', '?')}: {e}")
            row_out = row.copy()
            row_out["category"] = "Error"
            row_out["priority"] = "Low"
            row_out["reason"] = f"Crash during processing: {e}"
            row_out["flag"] = "ERROR"
            results.append(row_out)
            
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
