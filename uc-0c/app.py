import argparse
import csv


def route_row(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    category = row.get("category", "").strip()

    department = ""
    flag = "OK"

    if category == "Roads":
        department = "Road Maintenance"
    elif category == "Water":
        department = "Water Supply"
    elif category == "Sanitation":
        department = "Waste Management"
    elif category == "Other":
        department = "General Services"
        flag = "NEEDS_REVIEW"
    else:
        department = "General Services"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "department": department,
        "flag": flag
    }


def route_file(input_path, output_path):
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                results.append(route_row(row))
            except Exception:
                results.append({
                    "complaint_id": "",
                    "category": "",
                    "department": "",
                    "flag": "ERROR"
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "department", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Complaint Router")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    route_file(args.input, args.output)