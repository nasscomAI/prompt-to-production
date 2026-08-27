# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Accepts a single citizen complaint description and returns a structured classification with category, priority, reason, and ambiguity flag according to the fixed schema.
    input:
      type: object
      format:
        description_text: string — the raw complaint description from one CSV row
    output:
      type: object
      format:
        category: "string — exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
        priority: "string — exactly one of: Urgent, Standard, Low"
        reason: string — one sentence citing specific words from the input description
        flag: "string — NEEDS_REVIEW if genuinely ambiguous across categories, else empty string"
    error_handling:
      empty_or_missing_description: return flag as NEEDS_REVIEW, category as Other, priority as Low, reason as a sentence stating the description was absent or unreadable
      severity_keyword_present_but_low_priority_assigned: override priority to Urgent before returning; never allow Standard or Low when injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse appears in the description
      category_not_in_allowed_list: reject any generated category that is not in the ten allowed strings and reclassify; never return a variant, abbreviation, or invented sub-category
      ambiguous_description: set flag to NEEDS_REVIEW and select the closest matching allowed category; do not omit the flag or return a confident classification without it
      reason_missing_or_generic: regenerate reason until it contains at least one word or phrase directly lifted from the input description; a reason that does not reference the description text is invalid
      taxonomy_drift: validate the category string against the allowed list before returning; if the value drifted from the canonical spelling, correct it to the exact allowed string

  - name: batch_classify
    description: Reads a city complaint CSV file, applies classify_complaint independently to each row, and writes a results CSV containing the four classification fields for all rows.
    input:
      type: file
      format: CSV file at the path provided via --input argument; rows contain a complaint description column; category and priority_flag columns are absent and must not be read
    output:
      type: file
      format: CSV file written to the path provided via --output argument; contains exactly four columns — category, priority, reason, flag — with one row per input row and no additional or missing columns
    error_handling:
      input_file_not_found: halt execution and raise a descriptive error stating the missing file path; do not produce partial output
      row_count_mismatch: verify output row count equals input row count before writing; if a row was skipped or duplicated, reprocess and correct before finalising the file
      invalid_csv_structure: if required description column is missing or unreadable, mark all affected rows with flag NEEDS_REVIEW, category Other, priority Low, and a reason stating the row was malformed
      classify_complaint_failure_on_a_row: catch the per-row error, assign NEEDS_REVIEW flag and Other category for that row, log the row index and error, and continue processing remaining rows without halting the batch
      cross_row_contamination: each row must be classified independently; if any state or classification from a prior row is found to influence the current row, reset context between rows before reclassifying
      output_write_failure: raise a descriptive error with the target path; do not silently discard results
