skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and flag.
    input: A dictionary representing one CSV row containing complaint_id and description fields.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or unclear, category is set to "Other" and flag is set to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, classifies each complaint using classify_complaint, and writes results to an output CSV.
    input: Path to an input CSV file containing complaint rows.
    output: Output CSV file containing classified complaints with category, priority, reason, and flag.
    error_handling: If a row fails classification, it should still write the row with category "Other" and flag "NEEDS_REVIEW".