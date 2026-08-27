import argparse
import csv

def classify_complaint(row: dict) -> dict:

    text = str(row).lower()

    category = "General"
    priority = "Low"
    reason = "Default classification"
    flag = "OK"

    if "hospital" in text or "injury" in text:
        category = "Health"
        priority = "High"
        reason = "Health/safety complaint"

    elif "school" in text or "child" in text:
        category = "Education"
        priority = "Medium"
        reason = "Education related complaint"

    complaint_id = row.get("complaint_id", "UNKNOWN")

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path, output_path):

    results = []

    with open(input_path,'r',encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)

            except Exception:
                results.append({
                    "complaint_id":"ERROR",
                    "category":"Unknown",
                    "priority":"Low",
                    "reason":"Bad row",
                    "flag":"FAILED"
                })

    with open(output_path,'w',newline='',encoding='utf-8') as outfile:
        fields = ["complaint_id","category","priority","reason","flag"]

        writer = csv.DictWriter(outfile,fieldnames=fields)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input,args.output)

    print(f"Done. Results written to {args.output}")
