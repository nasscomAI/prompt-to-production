skills:
  - name: classify_complaint
    description: Classify a single complaint description into category, priority, reason, and flag.
    input: A single string — the complaint description text.
    output: A dictionary with keys: category (str), priority (str), reason (str), flag (str or empty).
    error_handling: If description is empty or None, return category "Other", priority "Low", reason "Empty description", flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to each row, and write the output CSV with classification columns added.
    input: Path to input CSV (must contain a 'description' column), path to output CSV.
    output: Output CSV written to disk with original columns plus category, priority, reason, flag.
    error_handling: If input file is missing or lacks a 'description' column, raise a clear error. If a single row fails classification, log the row index and continue processing remaining rows.
