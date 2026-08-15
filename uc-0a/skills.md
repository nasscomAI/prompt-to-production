skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row and classifies it into a standard category, determines priority based on safety triggers, supplies a justification citing text from description, and flags ambiguous rows.
    input: Dictionary with complaint fields (must include complaint_id, description, location, etc.).
    output: Dictionary containing complaint_id, category, priority, reason, flag.
    error_handling: When description is missing, empty, or unclassifiable, assigns category 'Other', priority 'Standard', reason 'Missing or insufficient description details.', and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, iterates through all rows invoking classify_complaint, handles file I/O errors and row formatting issues gracefully, and writes out the classified results CSV.
    input: File paths input_path (str) and output_path (str).
    output: Writes a CSV file containing columns complaint_id, category, priority, reason, flag.
    error_handling: Handles missing input files, malformed rows, and empty rows gracefully without halting execution.
