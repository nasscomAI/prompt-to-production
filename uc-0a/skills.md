# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dict representing one row (must include a "description" string field).
    output: A dict with keys category, priority, reason, flag.
    error_handling: If description is missing or empty, return category=Other, priority=Standard, reason="No description provided", flag=NEEDS_REVIEW instead of crashing.

  - name: batch_classify
    description: Reads an input CSV, classifies every row via classify_complaint, writes a results CSV.
    input: input_path (str path to CSV), output_path (str path to write CSV).
    output: Writes a CSV with all original columns plus category, priority, reason, flag. Returns None.
    error_handling: If a single row fails to classify (e.g. malformed data), log the row's complaint_id and continue processing remaining rows rather than stopping the whole batch.