import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row. STRICT RICE PROMPT.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    try:
        complaint_id = row.get("complaint_id", "").strip()
        complaint = row.get("description", "").strip().lower()

        if not complaint:
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": "Complaint description is empty.",
                "flag": ""
            }

        matched_categories = []
        words = [] # Words to cite for reason

        # 1. CATEGORY LOGIC (Exact mapping ensuring no drift or hallucination)
        if "pothole" in complaint or "crater" in complaint:
            matched_categories.append("Pothole")
            words.append("pothole/crater")
        if "flood" in complaint or "rain" in complaint:
            matched_categories.append("Flooding")
            words.append("flood/rain")
        if "drain" in complaint or "sewage" in complaint:
            matched_categories.append("Drain Blockage")
            words.append("drain/sewage")
        if "garbage" in complaint or "waste" in complaint:
            matched_categories.append("Waste")
            words.append("garbage/waste")
        if "noise" in complaint or "loud" in complaint:
            matched_categories.append("Noise")
            words.append("noise")
        if "road" in complaint or "road" in complaint:
            if "Pothole" not in matched_categories:
                matched_categories.append("Road Damage")
                words.append("road")
        if "heritage" in complaint:
            matched_categories.append("Heritage Damage")
            words.append("heritage")
        if "streetlight" in complaint:
            matched_categories.append("Streetlight")
            words.append("streetlight")
        if "heat" in complaint:
            matched_categories.append("Heat Hazard")
            words.append("heat")
            
        if len(matched_categories) == 0:
            category = "Other"
            reason_words = "None"
        else:
            category = matched_categories[0] # Pick most critical/first matched
            reason_words = words[0]

        # 2. PRIORITY LOGIC (Strict severity detection mapping)
        severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
        found_severity = [k for k in severity_keywords if k in complaint]
        
        if found_severity:
            priority = "Urgent"
            reason_words += f" and severity '{found_severity[0]}'"
        elif "problem" in complaint or "issue" in complaint:
            priority = "Standard"
        else:
            priority = "Low"

        # 3. REASON LOGIC (Explanation cited directly from description keywords)
        reason = f"Classified based on explicit keywords: {reason_words}."

        # 4. FLAG LOGIC (Ambiguity detection)
        flag = "NEEDS_REVIEW" if len(matched_categories) > 1 else ""

        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }

    except Exception as e:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": f"System error processing row: {e}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                pass

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)