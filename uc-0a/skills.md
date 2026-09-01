# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag.
    input: One complaint row's description field (string).
    output: A dict/row with four fields — category (one of the allowed exact values), priority (Urgent, Standard, or Low), reason (one sentence citing specific words from the description), flag (NEEDS_REVIEW or blank).
    error_handling: If the description does not clearly match any allowed category, set category to "Other" and flag to "NEEDS_REVIEW" rather than guessing.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results to the output CSV.
    input: Path to input CSV (test_[city].csv) with columns complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: Path to output CSV (results_[city].csv) with all original columns plus category, priority, reason, and flag.
    error_handling: If a row's description is empty or missing, still write a row with category "Other", priority "Low", reason noting the missing description, and flag "NEEDS_REVIEW" — never skip a row.