skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a structured output containing category, priority, reason, and flag according to the fixed schema.
    input:
      type: object
      format:
        description: A single row from the input CSV represented as a key-value object containing at minimum a complaint description string field.
        fields:
          - name: description
            type: string
            required: true
    output:
      type: object
      format:
        fields:
          - name: category
            type: string
            allowed_values:
              - Pothole
              - Flooding
              - Streetlight
              - Waste
              - Noise
              - Road Damage
              - Heritage Damage
              - Heat Hazard
              - Drain Blockage
              - Other
          - name: priority
            type: string
            allowed_values:
              - Urgent
              - Standard
              - Low
          - name: reason
            type: string
            format: One sentence citing specific words from the input description
          - name: flag
            type: string
            allowed_values:
              - NEEDS_REVIEW
              - ""
    error_handling:
      missing_description: Emit flag NEEDS_REVIEW, set category to Other, set priority to Low, and set reason to "Description field is empty or missing — cannot classify."
      ambiguous_category: Assign the closest matching allowed category or Other if no match is reasonable, and set flag to NEEDS_REVIEW with reason explaining the ambiguity using words from the description.
      severity_keyword_present: Always set priority to Urgent regardless of any other signal when any of the keywords injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse appear in the description — this must never be overridden.
      hallucinated_category: If the classification logic produces a category string not in the allowed list, replace it with Other and set flag to NEEDS_REVIEW.
      missing_reason: If a reason cannot be grounded in specific words from the description, set flag to NEEDS_REVIEW and return reason as "Insufficient description detail to justify classification."
      false_confidence: Never leave flag blank when the correct category is uncertain; ambiguity must always surface as NEEDS_REVIEW rather than a confident guess.

  - name: batch_classify
    description: Reads the city-specific input CSV, applies classify_complaint to every row, and writes the fully classified output CSV to the designated results path.
    input:
      type: file
      format:
        type: CSV
        path_pattern: ../data/city-test-files/test_[city].csv
        expected_rows: 15
        notes: The category and priority_flag columns are stripped from the input and must not be read or inferred from column position.
    output:
      type: file
      format:
        type: CSV
        path_pattern: uc-0a/results_[city].csv
        columns:
          - category
          - priority
          - reason
          - flag
        row_count: Must equal the number of input rows exactly
    error_handling:
      file_not_found: Abort with a descriptive error message stating the expected input path and that no processing was performed.
      row_count_mismatch: Abort and report which row index caused the failure; do not write a partial output file.
      taxonomy_drift: After classifying all rows, validate that identical complaint types received identical category strings; if drift is detected, log the offending rows and re-classify them to restore consistency before writing output.
      classify_complaint_failure: If classify_complaint raises an error on any row, catch the error, set that row's category to Other, priority to Low, flag to NEEDS_REVIEW, and reason to the caught error message, then continue processing remaining rows.
      empty_input_file: Abort with an error message indicating the input file contains no data rows and write no output file.
      output_directory_missing: Create the uc-0a/ directory if it does not exist before writing the results file.