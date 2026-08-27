skills:
  - name: classify_complaint
    description: Classifies one complaint row into the UC-0A schema with evidence-backed reasoning.
    input: "dict row containing complaint_id and complaint description text (plus optional row-local text fields)."
    output: "dict with keys: complaint_id, category, priority, reason, flag. category must be one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. priority must be one of: Urgent, Standard, Low. reason is one sentence citing complaint words. flag is NEEDS_REVIEW or blank."
    error_handling: "If required text is missing, empty, or category is ambiguous from row text alone, set category to Other, set flag to NEEDS_REVIEW, and provide a reason that cites available row text or explicitly notes missing description."

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes a complete output CSV.
    input: "input_path string to test_[city].csv with unlabeled complaints and output_path string for results_[city].csv."
    output: "CSV written at output_path with one output row per input row and columns: complaint_id, category, priority, reason, flag. Processing continues even if individual rows are problematic."
    error_handling: "Never crash on bad rows; for malformed or null rows, emit a fallback row with category Other, appropriate priority from detectable severity keywords if present else Standard, reason explaining the issue, and flag NEEDS_REVIEW."
