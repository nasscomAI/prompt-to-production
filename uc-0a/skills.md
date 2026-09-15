skills:
  - name: classify_complaint
    description: Classifies one municipal complaint into the fixed category and priority schema with an evidence-based reason.
    input: "One CSV complaint row as a mapping containing at least complaint_id and description; description is plain text."
    output: "A mapping with complaint_id, category, priority, reason, and flag, where category and priority use only the allowed exact values."
    error_handling: "If description is missing, blank, or does not support one allowed category, return category Other, a one-sentence reason citing the available text or missing description, and flag NEEDS_REVIEW. Set Urgent whenever a severity keyword is present."

  - name: batch_classify
    description: Reads a complaint CSV, classifies every row with classify_complaint, and writes a result CSV.
    input: "A readable UTF-8 CSV path with complaint rows and an output CSV path."
    output: "A UTF-8 CSV with one output row per readable input row and columns complaint_id, category, priority, reason, and flag."
    error_handling: "Reject an unreadable file or a CSV without headers. For individual malformed or incomplete rows, write an Other/NEEDS_REVIEW result instead of crashing or omitting that row; never create categories outside the fixed schema."
