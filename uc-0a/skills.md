# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag using deterministic keyword rules.
    input: One dict-like complaint row with at least complaint_id and description fields.
    output: Dict with keys complaint_id, category, priority, reason, and flag.
    error_handling: If description is empty or category is ambiguous, set category to Other and flag to NEEDS_REVIEW without raising exceptions.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint row by row, and writes a results CSV.
    input: Input CSV path and output CSV path.
    output: CSV containing one output row per input row with complaint_id, category, priority, reason, and flag.
    error_handling: Continues processing even if individual rows are malformed; emits safe fallback output rows instead of crashing.
