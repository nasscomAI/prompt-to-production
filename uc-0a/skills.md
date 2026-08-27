# skills.md

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into category, priority, reason, and optional flag.
    input: >
      dict with keys: complaint_id (str), description (str)
    output: >
      dict with keys: complaint_id, category, priority, reason, flag
      All values are strings. Flag is either "NEEDS_REVIEW" or empty string.
    error_handling: >
      If description is empty or missing, set category="Other", priority="Standard",
      reason="No description provided", flag="NEEDS_REVIEW". Never crash on any input.

  - name: batch_classify
    description: >
      Reads an input CSV of complaints, applies classify_complaint to every row, and writes
      a results CSV with complaint_id, category, priority, reason, and flag columns.
    input: >
      input_path (str): path to a CSV with at least complaint_id and description columns.
    output: >
      Writes a CSV at output_path with columns: complaint_id, category, priority, reason, flag.
    error_handling: >
      Skips rows with missing or non-string description after flagging them as NEEDS_REVIEW.
      Logs errors but continues processing remaining rows. Produces output even if some rows fail.
      Never crashes on malformed CSVs.
