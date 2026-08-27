# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into exactly one allowed
      category, assigns a priority based on severity keyword detection,
      produces a one-sentence reason citing specific words from the
      description, and sets a NEEDS_REVIEW flag when the complaint is
      genuinely ambiguous.
    input:
      type: object
      format: >
        A single complaint row represented as a key-value object containing
        at minimum a description field with the raw complaint text as a
        non-empty string.
    output:
      type: object
      format: >
        A key-value object with exactly four fields: category (one of
        Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
        Heritage Damage, Heat Hazard, Drain Blockage, Other), priority
        (one of Urgent, Standard, Low), reason (a single sentence
        referencing specific words from the input description), flag
        (NEEDS_REVIEW or empty string).
    error_handling:
      missing_description: >
        If the description field is absent or empty, set category to Other,
        priority to Low, reason to "No description provided for
        classification.", and flag to NEEDS_REVIEW.
      ambiguous_category: >
        If the description does not map clearly to a single allowed category,
        select the closest match, set flag to NEEDS_REVIEW, and state the
        ambiguity explicitly in the reason field — never assert confident
        classification on unclear input.
      severity_keyword_present: >
        If any severity keyword (injury, child, school, hospital, ambulance,
        fire, hazard, fell, collapse) appears in the description, priority
        must be set to Urgent regardless of any other signals — failure to
        do so is treated as a severity blindness error.
      invalid_category_attempt: >
        If the classifier would produce a category string not in the allowed
        list, it must fall back to Other and set flag to NEEDS_REVIEW rather
        than emit a non-schema value — hallucinated or variant category names
        are never written to output.
      missing_reason: >
        If a reason cannot be grounded in specific words from the description,
        the skill must not emit a generic or fabricated reason — instead it
        sets reason to a statement acknowledging the limitation and sets flag
        to NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads a city-specific input CSV, applies classify_complaint to each
      row independently, and writes a results CSV containing the original
      row data plus the four classification output fields for all rows.
    input:
      type: file
      format: >
        A CSV file at the path ../data/city-test-files/test_[city].csv
        containing at least 15 rows; the category and priority_flag columns
        are absent and must not be assumed present; each row must contain a
        complaint description field readable as a non-empty string.
    output:
      type: file
      format: >
        A CSV file written to uc-0a/results_[city].csv containing all
        original columns from the input plus four appended columns —
        category, priority, reason, flag — populated for every row with
        no rows omitted.
    error_handling:
      file_not_found: >
        If the input file path does not resolve, halt execution and raise a
        descriptive error stating the expected path — do not proceed with
        empty or partial output.
      malformed_csv: >
        If the CSV cannot be parsed or is missing the description column,
        halt and raise a schema error identifying the missing or malformed
        field — do not attempt classification on structurally invalid input.
      row_level_failure: >
        If classify_complaint raises an error or returns an invalid output
        for a specific row, write Other, Low, "Classification failed for
        this row.", and NEEDS_REVIEW for that row and continue processing
        remaining rows — a single row failure must not abort the batch.
      taxonomy_drift_prevention: >
        After all rows are classified, verify that category values are
        consistent across rows describing the same complaint type before
        writing output — if drift is detected, re-classify the affected rows
        rather than writing inconsistent values to the results file.
      partial_output_prevention: >
        The output CSV must contain exactly the same number of data rows as
        the input CSV — if any rows are missing from the output, treat this
        as a batch failure and raise an error before finalising the file.
