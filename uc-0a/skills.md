# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint into category, priority, reason, and
      flag using deterministic keyword matching — no LLM inference.
    input: >
      description: string — the raw complaint text from the "description" CSV column.
    output: >
      dict with four keys:
        category: str — one of Pothole, Flooding, Streetlight, Waste, Noise,
                   Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        priority: str — Urgent | Standard | Low
        reason:   str — one sentence citing at least one word from description
        flag:     str — NEEDS_REVIEW | "" (blank)
    validation_rules:
      - "category must be an exact member of the allowed list; no variants"
      - "priority must be Urgent if description contains any case-insensitive
         match for: injury, child, school, hospital, ambulance, fire, hazard,
         fell, collapse"
      - "reason must contain at least one word or phrase that appears in the
         original description"
      - "flag must be NEEDS_REVIEW when category is ambiguous between two or
         more allowed categories; otherwise blank"
      - "if description is empty or unclassifiable, category=Other,
         flag=NEEDS_REVIEW"
    error_handling: >
      On empty or missing description: return category=Other, priority=Standard,
      reason="No description provided.", flag=NEEDS_REVIEW.
      On unrecognized text: return category=Other, flag=NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Read an input CSV, apply classify_complaint to every row, and write the
      result CSV with exactly four columns in order.
    input: >
      input_path: str — filesystem path to the input CSV.
      output_path: str — filesystem path for the output CSV.
    output: >
      Writes a CSV file to output_path with columns:
        category, priority, reason, flag
      One row per input row, preserving row order.
    validation_rules:
      - "output row count must equal input row count"
      - "output must contain exactly four columns: category, priority, reason, flag"
      - "no input data rows may be modified or dropped"
      - "category values must pass exact-match validation against allowed list"
    error_handling: >
      If input file is missing: raise FileNotFoundError with clear message.
      If input file has no rows: write an empty CSV with the four header columns.
      If a row is missing the description column: treat description as empty.
