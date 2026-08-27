# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: A dictionary with keys: row_id (int), description (str), city (str).
    output: A dictionary with keys: row_id (int), category (str), priority (str), reason (str), flag (str or empty).
    error_handling: If description is empty or missing, set category to Other, priority to Low, reason to "No description provided", flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: input_path (str) — path to a CSV file with columns: row_id, description, city.
    output: Writes a CSV file with columns: row_id, category, priority, reason, flag. Returns the output path.
    error_handling: If input file is missing or malformed, raise FileNotFoundError with a descriptive message. If any row fails classification, log the row_id and continue processing remaining rows.
