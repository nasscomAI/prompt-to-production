skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag following the enforcement rules in agents.md.
    input: Dictionary representing one complaint row from the input CSV, containing at least complaint_id and description fields.
    output: Dictionary containing classification fields category (allowed taxonomy string), priority (Urgent, Standard, or Low), reason (one sentence citing specific words from description), and flag (NEEDS_REVIEW or blank).
    error_handling: If input data is genuinely ambiguous or lacks sufficient detail to determine a category, assign category 'Other' and flag 'NEEDS_REVIEW'. If any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) is present, escalate priority to 'Urgent'.

  - name: batch_classify
    description: Reads an input CSV containing complaint rows, applies classify_complaint to each row while preserving complaint_id, and writes results to an output CSV.
    input: File path string to input CSV containing complaint rows (e.g., test_[city].csv).
    output: File path string to output CSV containing complaint_id, category, priority, reason, and flag for each processed row.
    error_handling: Handles null, missing, or malformed rows without crashing; marks unresolvable rows with category 'Other' and flag 'NEEDS_REVIEW', and ensures valid results are produced even if individual rows encounter errors.
