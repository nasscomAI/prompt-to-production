# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and optional review flag.
    input: A single complaint description string from one CSV row.
    output: Object with fields: category (exact allowed string), priority (Urgent/Standard/Low), reason (one sentence citing specific words), flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or unreadable, output category: Other, priority: Standard, reason: "Description empty or unreadable", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of unclassified complaints, applies classify_complaint to each row, and writes the classified output CSV.
    input: Path to input CSV file (e.g. test_pune.csv) with complaint description column and stripped category/priority_flag columns.
    output: Path to output CSV file (e.g. results_pune.csv) with category, priority, reason, and flag columns populated for every row.
    error_handling: If the input CSV cannot be read or is missing the description column, halt and report the error — do not produce partial output.
