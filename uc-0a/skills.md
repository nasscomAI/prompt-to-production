skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a category, priority, reason, and optional review flag according to the fixed taxonomy and severity-keyword rules.
    input: >
      A single complaint record as a dict or CSV row containing at minimum a
      free-text description field (string, any length).
    output: >
      A dict with four fields:
        category (string) — exactly one of: Pothole, Flooding, Streetlight,
          Waste, Noise, Road Damage, Heritage Damage, Heat Hazard,
          Drain Blockage, Other;
        priority (string) — exactly one of: Urgent, Standard, Low;
        reason (string) — one sentence citing specific words from the description;
        flag (string) — NEEDS_REVIEW or blank.
    error_handling: >
      If the description is empty or missing, set category to Other,
      priority to Low, reason to "No description provided", and
      flag to NEEDS_REVIEW.
      If the description matches multiple categories with equal confidence,
      choose the most specific match and set flag to NEEDS_REVIEW.
      If the description contains a severity keyword (injury, child, school,
      hospital, ambulance, fire, hazard, fell, collapse), priority must be
      Urgent regardless of other signals — never downgrade to Standard or Low.
      Never produce a category value outside the allowed taxonomy; use Other
      rather than inventing a new label.
      Never output a composite or sub-category string (e.g., Pothole/Road Damage).

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the results to an output CSV.
    input: >
      File path (string) pointing to a CSV file structured as
      ../data/city-test-files/test_[city].csv; the file must contain a
      free-text description column; category and priority_flag columns may be
      absent (they are the target outputs).
    output: >
      A CSV file written to uc-0a/results_[city].csv containing all original
      columns plus four appended columns: category, priority, reason, flag —
      one output row for every input row, in the same order.
    error_handling: >
      If the input file does not exist or cannot be parsed, raise a descriptive
      error and halt without writing a partial output file.
      If an individual row is missing a description, apply classify_complaint
      error handling for that row (category: Other, priority: Low,
      reason: "No description provided", flag: NEEDS_REVIEW) and continue
      processing remaining rows.
      If the output path is not writable, raise a descriptive error and halt.
      Log a warning for every row where flag is set to NEEDS_REVIEW so that
      ambiguous cases are visible without manual inspection of the output file.
