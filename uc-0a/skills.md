# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint description into category, priority, reason, and flag.
    input: |
      - Type: dictionary/object
      - Format: {
          complaint_id: string,
          description: string
        }
    output: |
      - Type: dictionary/object
      - Format: {
          complaint_id: string,
          category: string (one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
          priority: string (Urgent, Standard, Low),
          reason: string (one sentence citing specific description words),
          flag: string (NEEDS_REVIEW or blank)
        }
    error_handling: |
      - If description is empty or missing: set category=Other, priority=Standard, reason='No description provided', flag=NEEDS_REVIEW.
      - If ambiguous classification: set category=Other, flag=NEEDS_REVIEW, provide reason explaining ambiguity.
      - Always return valid schema and avoid crashing.

  - name: batch_classify
    description: Read a complaints CSV, apply classify_complaint to each row, and write a classified CSV.
    input: |
      - Type: string paths
      - Format: (input_path: string, output_path: string), where input CSV has header (complaint_id, description).
    output: |
      - Type: file write
      - Format: output CSV with header (complaint_id, category, priority, reason, flag) and one output row per input row.
    error_handling: |
      - If input file is missing: raise FileNotFoundError with clear message.
      - If row has missing description: call classify_complaint fallback behavior and continue.
      - If a row produces an exception: log the issue, set flag=NEEDS_REVIEW, continue with other rows.
      - If output directory does not exist: create it.
      - Always write an output file, including rows with failures/flags.
