#skills.md
skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category and priority, citing source evidence and flagging any ambiguity.
    input: A dictionary representing a single complaint row (e.g., must contain 'complaint_id' and 'description' keys).
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling:
      - "If 'description' is null, empty, or missing, output category: 'Other', priority: 'Standard', reason: 'No complaint description provided.', and flag: 'NEEDS_REVIEW'."
      - "If multiple categories could apply (e.g., both drainage issues and road damage are mentioned), choose the most prominent category, populate the reason, and set flag: 'NEEDS_REVIEW'."
      - "If severity keywords are present, priority MUST be 'Urgent' regardless of ambiguity."

  - name: batch_classify
    description: Processes a CSV file of complaints, classifies each row, and writes the results to a new CSV file.
    input:
      input_path: Path to the source CSV file containing complaints (must have 'complaint_id' and 'description' columns).
      output_path: Path to write the output CSV containing classified complaints.
    output: Writes a CSV file containing columns: 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling:
      - "If the input file does not exist, raise a FileNotFoundError."
      - "If a row is empty or malformed, log/flag the failure and continue processing the rest of the file without crashing."
      - "If a required column like 'description' or 'complaint_id' is missing from the header, raise a ValueError."
