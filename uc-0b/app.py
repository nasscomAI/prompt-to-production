import argparse
import csv


def validate_row(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    text = row.get("complaint_text", "").strip()

    flag = "VALID"

    if not complaint_id:
        flag = "INVALID_ID"
    elif not text:
        flag = "NULL_TEXT"

    return {
        "complaint_id": complaint_id,
        "complaint_text": text,
        "flag": flag
    }


def validate_file(input_path, output_path):
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                results.append(validate_row(row))
            except Exception:
                results.append({
                    "complaint_id": "",
                    "complaint_text": "",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "complaint_text", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Data Validator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    validate_file(args.input, args.output)