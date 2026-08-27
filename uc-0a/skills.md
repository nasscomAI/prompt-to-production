# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: "Categorize a single complaint description and assign priority, reason, and flag according to the README schema."
    input: |
      A single complaint record with at minimum the field: `description` (string).
    output: |
      A dictionary/object with the exact keys:
        - `category` (string): one of the exact values: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other
        - `priority` (string): one of: Urgent · Standard · Low
        - `reason` (string): one sentence citing specific words or short phrases from the description
        - `flag` (string): `NEEDS_REVIEW` when ambiguous, otherwise blank
    error_handling: |
      - If `description` is empty or missing: return `category: Other`, `priority: Standard`, `reason: 'NEEDS_REVIEW: empty description'`, `flag: NEEDS_REVIEW`.
      - If category cannot be determined from the text: return `category: Other`, `flag: NEEDS_REVIEW` and provide a `reason` that cites the ambiguous text.
      - Always use exact category and priority strings from the schema; do not invent synonyms.

  - name: batch_classify
    description: "Read an input CSV of complaints, apply `classify_complaint` to each row, and write a validated output CSV.
    "
    input: |
      - `input_path` (string): path to the input CSV, e.g. `../data/city-test-files/test_[your-city].csv` (15 rows; `category` and `priority_flag` stripped).
      - `output_path` (string): path for the output CSV, e.g. `uc-0a/results_[your-city].csv`.
    output: |
      - Writes an output CSV with all original input columns plus the validated columns: `category`, `priority`, `reason`, `flag`.
      - Returns a short summary object: `{rows_processed: int, rows_flagged: int, errors: int}`.
    error_handling: |
      - If the input file cannot be read: raise an error and return a non-zero `errors` count in the summary.
      - For rows where `classify_complaint` sets `flag: NEEDS_REVIEW`, include them in `rows_flagged` and do not modify original text.
      - Ensure output CSV uses exactly the allowed category and priority strings; convert any internal variants to the canonical form or set `Other` with `NEEDS_REVIEW`.

notes: |
  - Severity keywords that must trigger `Urgent`: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
  - `classify_complaint` must always populate `reason` with a one-sentence justification citing words from the `description`.
  - Follow the repository's commit formula when fixing failures: `UC-0A Fix [failure mode]: [why it failed] → [what you changed]`.

  - name: classify_complaint
    description: Categorizes a complaint description into predefined categories.
    input: Complaint description as a plain text string.
    output: A dictionary with keys 'category' (string) and 'justification' (string).
    error_handling: Returns 'category': 'Other' and 'justification': 'NEEDS_REVIEW' if the input is ambiguous or empty.

  - name: prioritize_complaint
    description: Assigns a priority level to a complaint based on its description.
    input: Complaint description as a plain text string.
    output: A dictionary with keys 'priority' (string) and 'justification' (string).
    error_handling: Returns 'priority': 'Medium' and 'justification': 'Default priority assigned' if the input is ambiguous or empty.
