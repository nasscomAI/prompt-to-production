skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag according to the fixed schema and severity keyword rules.
    input:
      type: object
      format: >
        A single complaint row containing at minimum a description field
        (free text) and any other non-stripped columns from the input CSV
        (e.g. complaint ID, city, date). The category and priority_flag
        fields are absent and must not be assumed.
    output:
      type: object
      format: >
        A single object with four fields: category (one exact string from
        the allowed schema list: Pothole, Flooding, Streetlight, Waste,
        Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage,
        Other), priority (one of Urgent, Standard, Low), reason (one
        sentence citing specific words from the description), and flag
        (NEEDS_REVIEW or blank).
    error_handling: >
      If the description is missing or empty, set category to Other,
      priority to Low, reason to state that no description was provided,
      and flag to NEEDS_REVIEW. If a severity keyword (injury, child,
      school, hospital, ambulance, fire, hazard, fell, collapse) is
      present in the description, priority must always be set to Urgent
      regardless of category, to prevent severity blindness. If the
      complaint could plausibly belong to more than one category or does
      not clearly match any allowed category, do not guess or invent a
      new sub-category — select the closest allowed category (using
      Other only if no reasonable match exists) and set flag to
      NEEDS_REVIEW rather than returning a confident classification. The
      reason field must never be left blank; if no specific words in the
      description support a clear classification, the reason must state
      that the classification is uncertain and cite whatever partial
      evidence exists. Never output a category string that is not exactly
      one of the allowed values, and never vary spelling, casing, or
      phrasing of a category across calls for the same complaint type.

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint to every row, and writes a single output CSV file with all classified fields populated.
    input:
      type: file
      format: >
        Path to a CSV file at ../data/city-test-files/test_[your-city].csv
        containing 15 complaint rows per city, with category and
        priority_flag columns stripped.
    output:
      type: file
      format: >
        A CSV file written to uc-0a/results_[your-city].csv containing
        all original input rows plus the four classified columns:
        category, priority, reason, and flag, in the same row order as
        the input.
    error_handling: >
      If the input file cannot be found or opened, halt and report the
      error rather than producing a partial or empty output file. If a
      row is malformed or missing required fields, still write that row
      to the output with category set to Other, priority set to Low,
      reason explaining the row was malformed, and flag set to
      NEEDS_REVIEW, rather than skipping or dropping the row. Every input
      row must produce exactly one output row — no rows may be dropped,
      merged, or duplicated. If classify_complaint returns a category not
      in the allowed schema list, batch_classify must reject that result,
      coerce it to Other, and set flag to NEEDS_REVIEW rather than writing
      the invalid category to the output file.