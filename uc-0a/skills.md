# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: One complaint row as a dict with at minimum a `description` string field.
    output: Dict with four fields — `category` (str), `priority` (str), `reason` (str), `flag` (str or blank).
    error_handling: If description is empty or missing, return category: Other, priority: Low, reason: "No description provided.", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Path to input CSV file (str); path to output CSV file (str). Input CSV must have a `description` column.
    output: Output CSV written to disk with all original columns plus `category`, `priority`, `reason`, and `flag` columns appended.
    error_handling: If the input file is missing or unreadable, raise FileNotFoundError with the file path. If a row fails classification, write category: Other, flag: NEEDS_REVIEW for that row and continue processing remaining rows.
