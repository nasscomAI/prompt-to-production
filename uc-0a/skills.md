skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flags ambiguity.
    input: A dictionary containing complaint data (complaint_id, description, etc.)
    output: A dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: If input text is entirely missing or illegible, set category to Other, priority to Low, and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes results to an output CSV.
    input: File paths for input CSV and output CSV.
    output: None (writes a CSV file to disk).
    error_handling: If a row fails to parse, it must flag nulls, not crash, and continue processing remaining rows. Output is generated even if some rows fail.
