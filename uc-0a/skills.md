skills:
  - name: classify_complaint
    description: >
      Accepts a single complaint row and returns exactly four classification
      fields — category, priority, reason, and flag — strictly conforming
      to the UC-0A schema.
    input:
      type: object
      format: >
        A single row represented as a key-value mapping containing at minimum
        a description field with the raw complaint text as a non-empty string;
        all other columns from the source CSV may be present and are passed
        through unchanged.
    output:
      type: object
      format: >
        The original input fields plus four appended fields: category as one
        of exactly ten allowed strings (Pothole, Flooding, Streetlight, Waste,
        Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage,
        Other); priority as one of Urgent, Standard, or Low; reason as a
        single sentence that references specific words from the input
        description; flag as the exact string NEEDS_REVIEW or blank.
    error_handling:
      missing_description: >
        If the description field is absent or blank, set category to Other,
        priority to Low, reason to "No description provided — cannot classify",
        and flag to NEEDS_REVIEW; do not halt or skip the row.
      invalid_category_temptation: >
        If no allowed category fits the description cleanly, assign Other
        rather than inventing or approximating a category string; never output
        a category value outside the ten allowed strings.
      severity_keyword_present: >
        If any of the severity keywords (injury, child, school, hospital,
        ambulance, fire, hazard, fell, collapse) appear in the description,
        priority must be set to Urgent regardless of any other signal; failure
        to detect a keyword is treated as a severity-blindness error.
      ambiguous_category: >
        If the description could reasonably map to more than one allowed
        category, assign the most likely category and set flag to
        NEEDS_REVIEW; never omit the flag when genuine ambiguity exists and
        never express confident classification without it.
      missing_reason: >
        A reason field must always be populated; if the description is too
        vague to support a specific citation, reason must state that explicitly
        (e.g. "Description too vague to cite specific evidence") and flag must
        be set to NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads a 15-row input CSV with category and priority_flag columns
      stripped, applies classify_complaint to every row, and writes the
      fully classified results to the designated output CSV.
    input:
      type: file
      format: >
        A UTF-8 CSV file located at ../data/city-test-files/test_[city].csv
        containing 15 rows; the category and priority_flag columns are absent
        and must not be assumed present; all other original columns are
        preserved as-is and passed to classify_complaint unchanged.
    output:
      type: file
      format: >
        A UTF-8 CSV file written to uc-0a/results_[city].csv containing
        exactly 15 rows with all original columns plus four appended columns
        — category, priority, reason, flag — where every cell conforms to
        the classify_complaint output contract; no rows may be skipped or
        reordered.
    error_handling:
      file_not_found: >
        If the input file path does not resolve, halt immediately and emit
        a descriptive error message stating the expected path; do not create
        an empty output file.
      wrong_row_count: >
        If the input file contains fewer or more than 15 rows, log a warning
        with the actual count and continue processing all rows present; do
        not truncate or pad to 15.
      per_row_failure: >
        If classify_complaint raises an error on a specific row, write that
        row to the output with category set to Other, priority to Low, reason
        set to "Classification failed — see error log", and flag set to
        NEEDS_REVIEW; continue processing remaining rows without halting.
      taxonomy_drift_prevention: >
        After all rows are classified, scan the output category column and
        verify that complaint descriptions of the same type have not received
        different category strings across rows; if drift is detected, log
        each affected row index and the conflicting category values before
        writing the output file.
      output_write_failure: >
        If the output file cannot be written to the target path, emit a
        descriptive error message stating the attempted path and the reason
        for failure; do not silently discard the classified results.