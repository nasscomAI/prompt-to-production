# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a structured output with category, priority, reason, and flag.
    input: One complaint description string (plain text from the description field of a CSV row).
    output: >
      A structured record with four fields:
        - category: exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
          Heritage Damage, Heat Hazard, Drain Blockage, Other
        - priority: exactly one of Urgent, Standard, Low
        - reason: one sentence citing specific words from the input description
        - flag: NEEDS_REVIEW if category is ambiguous, otherwise blank
    error_handling: >
      If the category cannot be determined from the description alone, output
      category: Other and flag: NEEDS_REVIEW. Never invent a category outside the
      allowed list. If severity keywords (injury, child, school, hospital, ambulance,
      fire, hazard, fell, collapse) are present, always set priority to Urgent
      regardless of other signals.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a classified output CSV.
    input: >
      A CSV file path (string) where each row contains at minimum a complaint description
      field. The category and priority_flag columns are absent and must be produced.
    output: >
      A CSV file written to the specified output path containing all original columns
      plus the four classification fields: category, priority, reason, flag.
    error_handling: >
      Rows where classification is ambiguous are written with category: Other and
      flag: NEEDS_REVIEW rather than skipped or errored. If the input file is missing
      or unreadable, the skill raises an error and writes nothing.
