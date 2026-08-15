skills:
  - name: classify_complaint
    description: Classifies a single complaint record into an authorized category, priority level, cited justification reason, and review flag based on strict taxonomy and safety rules.
    input: dict containing complaint fields (complaint_id, date_raised, city, ward, location, description, reported_by, days_open)
    output: dict containing keys (complaint_id, category, priority, reason, flag)
    error_handling: If input description is empty, missing, or genuinely ambiguous, assigns category 'Other', flag 'NEEDS_REVIEW', and sets a descriptive reason without crashing.

  - name: batch_classify
    description: Reads an input CSV of municipal complaints, validates rows, executes classify_complaint for each record, and writes standard results to an output CSV.
    input: input_path (str path to input CSV), output_path (str path to destination CSV)
    output: None (writes output CSV file containing complaint_id, category, priority, reason, flag)
    error_handling: Handles missing files, malformed rows, or invalid values gracefully; logs errors, flags failed rows as 'NEEDS_REVIEW', and guarantees output file generation.
