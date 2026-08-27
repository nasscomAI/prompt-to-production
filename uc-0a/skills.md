skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag using the fixed schema.
    input:
      type: object
      format: >
        A single row with at minimum a complaint description string field; category and
        priority_flag fields are absent and must not be read even if present.
    output:
      type: object
      format: >
        Four fields — category (one of: Pothole, Flooding, Streetlight, Waste, Noise,
        Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority
        (Urgent, Standard, or Low), reason (one sentence citing words from the description),
        flag (NEEDS_REVIEW or blank).
    error_handling:
      - condition: empty_or_missing_description
        description: "Empty or missing description — cannot classify"
        response:
          category: Other
          priority: Low
          reason: "No description provided — cannot classify."
          flag: NEEDS_REVIEW

      - condition: model_non_json_output
        description: "Model returned non-JSON output — justification gap"
        response:
          category: Other
          priority: Low
          reason: "Model returned non-JSON output — justification gap."
          flag: NEEDS_REVIEW

      - condition: api_error
        description: "API call failed — classification could not complete"
        response:
          category: Other
          priority: Low
          reason: "API error during classification."
          flag: NEEDS_REVIEW

      - condition: no_matching_category
        description: "No category in the allowed list fits the description — use Other"
        response:
          category: Other

      - condition: ambiguous_category
        description: "Description matches multiple categories with equal confidence"
        response:
          flag: NEEDS_REVIEW

      - condition: reason_not_groundable
        description: "Reason absent or cannot be grounded in description words"
        response:
          reason: "Classification reason absent — justification gap detected."
          flag: NEEDS_REVIEW

      - condition: severity_keyword_present
        description: "Severity keyword present — keyword presence alone triggers Urgent"
        response:
          priority: Urgent

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input:
      type: file
      format: >
        CSV file at the path provided via --input flag; must contain a complaint description
        column per row; category and priority_flag columns are stripped and must not be used.
    output:
      type: file
      format: >
        CSV file written to the path provided via --output flag; contains all original columns
        plus four appended fields per row: category, priority, reason, flag; one output row
        per input row with no omissions.
    error_handling:
      - condition: input_file_not_found
        description: "Input file not found or unreadable"
        action: exit
        message: "Error: Input file not found: {path}"

      - condition: no_description_column
        description: "Input file has no description column"
        action: exit
        message: "Error: Input file has no 'description' column: {path}"

      - condition: all_descriptions_empty
        description: "All description values are empty — nothing to classify"
        action: exit
        message: "Error: All 'description' values are empty in: {path}"

      - condition: output_not_writable
        description: "Output path is not writable before processing begins"
        action: exit
        message: "Error: Output path is not writable: {path}"

      - condition: row_classification_failure
        description: "Individual row classification fails — write NEEDS_REVIEW, never halt the batch"
        action: continue
        response:
          category: Other
          priority: Low
          reason: "Unexpected error during classification."
          flag: NEEDS_REVIEW

      - condition: taxonomy_drift
        description: "Same complaint type produced different category strings across rows"
        action: normalize
