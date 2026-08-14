# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and review flag using the enforcement rules from agents.md.
    input: |
      Dict with keys: {
        "id": str (optional complaint ID),
        "description": str (complaint text, required)
      }
    output: |
      Dict with keys: {
        "id": str (same as input),
        "category": str (one of 10 allowed values or "Other"),
        "priority": str ("Urgent", "Standard", or "Low"),
        "reason": str (one sentence citing 2–3 words from description),
        "flag": str ("NEEDS_REVIEW" or empty string)
      }
    error_handling: |
      If description is empty or None, return category="Other", priority="Standard", reason="No description provided", flag="NEEDS_REVIEW".
      If description length < 5 chars, treat as insufficient context: category="Other", flag="NEEDS_REVIEW".
      If classification confidence is low (multiple categories equally plausible), set flag="NEEDS_REVIEW" and choose most likely category.
      Severity keywords are case-insensitive matching on whole words only (not substrings).

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes classified results to output CSV.
    input: |
      Dict with keys: {
        "input_file": str (path to CSV with required column "description", optional "id"),
        "output_file": str (path to write results CSV)
      }
    output: |
      Dict with keys: {
        "status": str ("success" or "error"),
        "rows_processed": int,
        "rows_flagged": int (count of NEEDS_REVIEW),
        "output_path": str,
        "errors": list of str (any per-row errors encountered)
      }
    error_handling: |
      If input_file does not exist or is not readable, return status="error" with descriptive message.
      If "description" column is missing, return status="error".
      If output_file directory does not exist, create it or return status="error".
      Missing "id" column: auto-generate as "row_N" (1-indexed).
      On per-row classification failure, log error, write partial row with category="Other", flag="NEEDS_REVIEW", and continue processing remaining rows.
      On successful completion, always return status="success" even if some rows were flagged.
