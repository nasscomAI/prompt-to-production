# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag.
    input: A dictionary-like row with at least a description field and optional complaint_id.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: Returns a safe fallback with category Other, priority Standard, and NEEDS_REVIEW when the description is missing or ambiguous.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes a results CSV.
    input: A path to an input CSV file and a path for the output CSV file.
    output: A CSV file containing complaint_id, category, priority, reason, and flag for every input row.
    error_handling: Continues processing even when a row fails and writes a fallback row instead of crashing.
