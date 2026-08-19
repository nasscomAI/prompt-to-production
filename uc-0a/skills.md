# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Accepts a single complaint row dictionary, extracts description text, classifies category against taxonomy, assesses priority based on severity keywords, generates a one-sentence reason citing matched terms, and sets flag (NEEDS_REVIEW or blank).
    input: A dictionary representing a single CSV row with keys 'complaint_id', 'description', etc.
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: If description is missing or null, set category to 'Other', priority to 'Standard', reason to 'No description provided', and flag to 'NEEDS_REVIEW' without crashing.

  - name: batch_classify
    description: Reads an input CSV file of complaint rows, applies classify_complaint to each row in sequence, and writes the structured classification results to an output CSV file.
    input: File paths input_path (str) and output_path (str).
    output: Writes output CSV file with columns complaint_id, category, priority, reason, flag.
    error_handling: Handles missing input files gracefully by logging an error and writing empty CSV with proper headers. Skips malformed individual rows while processing remaining valid rows.