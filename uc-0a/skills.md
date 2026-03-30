skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and flag based on the complaint description against the predefined taxonomy.
    input: "Dict with keys: complaint_id and description (the complaint text). Description is a string that may be empty."
    output: "Dict with keys: category (str), priority (str), reason (str), flag (str). All four keys must be present."
    error_handling: "If description is missing, empty, or cannot be mapped to any category despite attempting classification, set category to Other and flag to NEEDS_REVIEW. If description contains severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse), priority is Urgent; otherwise Standard. Reason must always cite specific words from the description."

  - name: batch_classify
    description: Reads input CSV with complaint records, applies classify_complaint to each row, and writes output CSV with all classification results.
    input: "Path to input CSV file with columns: complaint_id, description. Paths are strings."
    output: "CSV file at output path with columns: complaint_id, category, priority, reason, flag. One row per input complaint."
    error_handling: "If input file is missing or malformed, raise error with clear message. If a row has missing description, classify it with category=Other, flag=NEEDS_REVIEW. If a row cannot be classified, flag it and continue processing remaining rows. Write all results to output file even if some rows failed classification."
