skills:
  - name: classify_complaint
    description: Analyzes a single civic complaint and extracts classification details based on RICE rules.
    input: A dictionary containing complaint_id and description from a CSV row.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If description is null, empty, or unparseable, return category: "Other", priority: "Low", reason: "Missing description", flag: "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: String path to the input CSV and string path to the output CSV.
    output: A written CSV file with columns: complaint_id, category, priority, reason, flag.
    error_handling: Should not crash on bad rows. Flags nulls. Produces output even if some rows fail.
