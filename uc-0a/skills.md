skills:
  - name: classify_complaint
    description: >
      Accepts a single complaint description string and returns exactly four
      classification fields — category, priority, reason, and flag — according
      to the fixed taxonomy and severity keyword rules.
    input:
      type: string
      format: >
        A plain-text citizen complaint description extracted from one row of the
        input CSV. The description field must be non-empty. No other columns are
        required or permitted as input to this skill.
    output:
      type: object
      format: >
        A structured record with exactly four fields:
        - category: one of exactly — Pothole, Flooding, Streetlight, Waste,
          Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage,
          Other — reproduced with exact capitalisation and spacing.
        - priority: one of exactly — Urgent, Standard, Low. Must be Urgent if
          any of the following keywords appear in the description: injury,
          child, school, hospital, ambulance, fire, hazard, fell, collapse.
        - reason: one sentence citing specific words from the input description
          that justify the category and priority assignment.
        - flag: the string NEEDS_REVIEW if the description maps with equal
          plausibility to more than one allowed category, otherwise an empty
          string.
    error_handling:
      - If the description field is empty or missing, return category: Other,
        priority: Low, reason: "Description field was empty — no content to
        classify.", flag: NEEDS_REVIEW.
      - If the description text does not clearly match any of the nine named
        categories, assign category: Other rather than inventing a new label or
        compound name.
      - If a severity keyword is present but the context makes the complaint
        ambiguous across categories, still set priority to Urgent and set flag
        to NEEDS_REVIEW — the severity rule is never overridden by ambiguity.
      - If the description is genuinely ambiguous across two or more categories
        with equal plausibility, set flag to NEEDS_REVIEW and select the
        single best-fit category; do not output a compound or hybrid category
        name.
      - Never use hedging language in the reason field. If a confident one-
        sentence reason citing the input text cannot be written, set flag to
        NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads an input CSV file of complaint rows, applies classify_complaint to
      each row independently, and writes a results CSV file containing the
      original columns plus the four classification fields.
    input:
      type: file
      format: >
        A UTF-8 CSV file whose rows each contain at minimum a complaint
        description column. The category and priority_flag columns are absent
        from the input and must not be assumed to exist. The file path is
        supplied via the --input command-line argument. Expected row count is
        15 rows per city file; the skill must not assume a fixed row count.
    output:
      type: file
      format: >
        A UTF-8 CSV file written to the path supplied via the --output
        command-line argument. Each row preserves all original input columns
        and appends four new columns in this order: category, priority, reason,
        flag. Column headers must use these exact names. No rows may be
        dropped, reordered, or merged. The output file must contain exactly the
        same number of data rows as the input file.
    error_handling:
      - If the input file path does not exist or cannot be read, halt
        immediately and print an error message stating the file path and reason;
        do not write a partial output file.
      - If the input file is missing the description column, halt immediately
        and print a schema error listing the expected column name; do not
        attempt to classify.
      - If any individual row's description field is empty, pass it to
        classify_complaint which will return category: Other, priority: Low,
        reason citing the empty field, and flag: NEEDS_REVIEW — the row is
        still written to the output file and the batch continues.
      - If the output file path cannot be written (permissions, missing
        directory), halt immediately after processing and print a write error;
        do not silently discard results.
      - Each row must be classified independently. State or patterns from one
        row must not influence the classification of any subsequent row.
