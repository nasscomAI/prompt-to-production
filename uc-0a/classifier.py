import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    raise NotImplementedError("Build this using your AI tool + RICE prompt")

    complaint_id = row["complaint_id"]
    description = row["description"].lower()

    category = "other"
    priority = "low"
    reason = "no critical keywords"
    flag = "ok"

    if "pothole" in description or "collapsed" in description or "crater" in description:
        category = "road_damage"

    elif "flood" in description or "drain" in description or "blocked" in description:
        category = "water_logging"

    elif "garbage" in description or "waste" in description or "overflow" in description:
        category = "sanitation"

    if "ambulance" in description or "hospital" in description or "hospitalised" in description or "risk" in description or "school" in description:
        priority = "high"
        reason = "public safety risk"

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
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    raise NotImplementedError("Build this using your AI tool + RICE prompt")

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        results = []

        for row in reader:
            result = classify_complaint(row)
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
