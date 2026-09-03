# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category + priority + reason + flag using the UC-0A schema.
    input: >
      A single CSV row as a dict. Required fields: complaint_id,
      date_raised, city, ward, location, description, reported_by,
      days_open. Only the description (and secondarily location) are
      used for classification.
    output: >
      A dict with four keys: category (one of the 10 enum strings),
      priority ("Urgent" | "Standard" | "Low"), reason (a non-empty
      sentence quoting words from the description), flag ("NEEDS_REVIEW"
      or "").
    error_handling: >
      If the description is empty, return category=Other, priority=Low,
      reason="Empty description; cannot classify.", flag=NEEDS_REVIEW.
      If the description matches multiple categories with comparable
      evidence, return the best-evidence category and set
      flag=NEEDS_REVIEW. If no category is a strong match, return
      category=Other with flag=NEEDS_REVIEW. Never return a category
      outside the 10-value enum, and never return Standard or Low
      when a severity keyword is present in the description.

  - name: batch_classify
    description: Read the input CSV, classify every row with classify_complaint, write the output CSV.
    input: >
      A path to the input CSV (--input) and a path for the output CSV
      (--output). The input must contain the 8 schema columns.
    output: >
      A CSV at --output with the same complaint_id plus 4 new columns:
      category, priority, reason, flag. One output row per input row,
      in the same order.
    error_handling: >
      If the input file is missing, empty, or missing required
      columns, fail loudly with a clear message and a non-zero exit.
      After classification, before writing, scan the output: any row
      whose description contains a severity keyword but whose priority
      is not Urgent is a hard error — refuse to write. Any category
      value outside the 10-value enum is a hard error — refuse to
      write. The city named in the output filename should match the
      --output path's stem when supplied; if the README examples use
      results_[city].csv the agent must follow that convention.
