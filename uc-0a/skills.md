# UC-0A skills

skills:
  - name: classify_complaint
    description: Classify a single complaint row into `category`, `priority`, `reason`, and `flag` following UC-0A schema and enforcement rules.
    input: |
      A single CSV row as a dict/object with at least the `description` field. Other fields (location, timestamp) may be present and are available but optional.
    output: |
      A dict/object with exactly the keys: `category` (string), `priority` (string), `reason` (string), `flag` (string or empty).
      - `category`: one of the exact allowed strings: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other
      - `priority`: Urgent · Standard · Low
      - `reason`: one sentence citing specific words/phrases from the `description`
      - `flag`: `NEEDS_REVIEW` or blank
    error_handling: |
      - If `description` is empty or missing → return `category: Other`, `priority: ` (blank), `reason: 'No description provided'`, `flag: NEEDS_REVIEW`.
      - If multiple categories appear ambiguous → set `category: Other` and `flag: NEEDS_REVIEW` (do not fabricate a more specific category).
      - Always return all four keys; `flag` may be blank but must exist.
    enforcement: |
      - Enforce exact category strings (no synonyms, case must match allowed values).
      - If any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) appears in `description`, set `priority: Urgent`.
      - `reason` must include at least one exact token or short phrase from the `description` and be a single sentence.
    examples: |
      Input: {"description": "Small child fell into an open pothole near the school entrance."}
      Output: {"category":"Pothole","priority":"Urgent","reason":"Mentions 'child fell' near 'school entrance'.","flag":""}

  - name: batch_classify
    description: Read an input CSV of complaints, apply `classify_complaint` to each row, validate outputs, and write the results CSV.
    input: |
      Path to an input CSV file with rows matching the city test format (see `../data/city-test-files`).
    output: |
      Writes `uc-0a/results_[city].csv` containing all original columns plus the appended `category`, `priority`, `reason`, and `flag` columns. Returns a summary dict with counts (rows_processed, flagged_count, errors).
    error_handling: |
      - Rows that trigger `NEEDS_REVIEW` are written with `flag=NEEDS_REVIEW` and counted in `flagged_count`.
      - I/O errors should raise an explicit error and not write partial outputs; implement atomic write (write temp file then rename).
    enforcement: |
      - Validate every output row with `schema_enforcer` before final write; abort run if systemic schema violations exceed a threshold (e.g., >5% rows).
    examples: |
      Run: `python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv`

  - name: schema_enforcer
    description: Rule-based validator that checks and sanitizes classifier outputs before they are written to disk.
    input: A classified row (dict) produced by `classify_complaint`.
    output: The validated (and possibly normalized) row; or a marker indicating `NEEDS_REVIEW`.
    error_handling: |
      - Auto-normalize whitespace and trim values.
      - If category is not one of the allowed strings, set `category: Other` and `flag: NEEDS_REVIEW`.
      - If `reason` is missing or doesn't quote source text, set `flag: NEEDS_REVIEW`.

  - name: human_reviewer
    description: Manual review workflow for rows marked `NEEDS_REVIEW` to resolve ambiguity and provide justification for training data.
    input: A CSV or list of rows with `flag=NEEDS_REVIEW`.
    output: Updated rows with corrected `category`, `priority`, `reason`, and blanked `flag` after review.
    error_handling: |
      - Record reviewer id and rationale in extra columns; do not alter original description.

notes: |
  - The two core skills required by the UC are `classify_complaint` and `batch_classify`; the other skills are helpers recommended by `agents.md` to improve reliability and traceability.
  - Tests should exercise the severity keyword behavior, empty-description handling, exact category enforcement, and the `NEEDS_REVIEW` flag path using the city test CSVs in `../data/city-test-files`.

