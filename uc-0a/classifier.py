def classify_complaint(row: dict) -> dict:
    text = row.get("complaint_text", "").lower()

    category = "general"
    priority = "low"
    reason = "general complaint"
    flag = "no"

    if not text:
        flag = "missing_text"
        reason = "complaint text missing"

    elif "refund" in text or "payment" in text:
        category = "billing"
        priority = "high"
        reason = "payment issue"

    elif "delay" in text:
        category = "service"
        priority = "medium"
        reason = "service delay"

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }
    def batch_classify(input_path: str, output_path: str):

    results = []

    with open(input_path, "r") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id"),
                    "category": "error",
                    "priority": "low",
                    "reason": "processing error",
                    "flag": "error"
                })

    with open(output_path, "w", newline="") as outfile:
        fieldnames = ["complaint_id","category","priority","reason","flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)
