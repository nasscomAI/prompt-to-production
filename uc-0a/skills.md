# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row into `category`, `priority`, `reason`, and `flag`.
    input:
      type: object
      fields:
        - id: optional (string or number)
        - description: required (string) — the complaint text to classify
        - other_fields: optional (object) — any additional metadata from the row
    output:
      type: object
      fields:
        - category: string (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other)
        - priority: string (one of: Urgent, Standard, Low)
        - reason: string (one sentence citing specific words from `description`)
        - flag: string ("NEEDS_REVIEW" or blank)
    error_handling:
      - If `description` is missing or empty: return an error object and set `flag` to "NEEDS_REVIEW".
      - If multiple categories are equally plausible: set `category` to "Other" and `flag` to "NEEDS_REVIEW" and include a reason describing the ambiguity.
      - If severity keywords are present, force `priority` to "Urgent".

  - name: batch_classify
    description: Read an input CSV, run `classify_complaint` on each row, and write an output CSV with classification fields appended.
    input:
      type: object
      fields:
        - input_path: string — relative path to input CSV (rows expected to include a `description` column)
        - output_path: string — relative path where output CSV will be written
    output:
      type: object
      fields:
        - output_path: string — the actual path written
        - summary: object — counts {total, classified, needs_review, errors}
    error_handling:
      - Skip rows with missing description, increment `errors` and write a row with `flag` "NEEDS_REVIEW".
      - If the input file cannot be read or parsed, raise a clear error and do not write an output file.
      - Always preserve original row columns and append `category`, `priority`, `reason`, `flag`.

notes: |
  - Implementations of `classify_complaint` must enforce the exact category strings listed in the README and must include a `reason` that cites text from the complaint.
  - `batch_classify` should be idempotent: running it twice on the same input should produce the same output (except for timestamped logs).
