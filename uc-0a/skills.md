skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a category, priority, reason, and review flag.
    input: "One complaint record (dict/row) with a 'description' text field, from the input CSV."
    output: "A dict with four fields: category (string, one of the fixed list), priority (Urgent/Standard/Low), reason (one sentence citing description words), flag (NEEDS_REVIEW or blank)."
    error_handling: >
      If the description is empty or too vague to match any category confidently,
      set category to "Other" and flag to "NEEDS_REVIEW" rather than guessing.
      If severity keywords (injury, child, school, hospital, ambulance, fire, hazard,
      fell, collapse) are present, priority must be forced to "Urgent" regardless of
      other signals.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results to the output CSV.
    input: "Path to input CSV file (test_[city].csv) with complaint rows, category and priority_flag columns stripped."
    output: "Output CSV file (results_[city].csv) with all original columns plus category, priority, reason, and flag columns filled in for every row."
    error_handling: >
      If the input file is missing or unreadable, raise a clear error and stop
      rather than producing a partial output file. If a row is malformed (missing
      description), still output a row with category "Other", flag "NEEDS_REVIEW",
      and a reason noting the row was incomplete — never skip a row silently.