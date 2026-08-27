# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen-complaint row into a category, priority, reason, and review flag.
    input: >
      A single CSV row containing at minimum a complaint description text field.
      May also include metadata columns (e.g., location, date, complainant ID).
    output: >
      A dictionary / row with exactly four fields:
        - category: One of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        - priority: One of Urgent, Standard, Low. Must be Urgent if description contains any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse).
        - reason: Exactly one sentence citing specific words from the description that justify the chosen category and priority.
        - flag: NEEDS_REVIEW if the category is genuinely ambiguous; blank otherwise.
    error_handling: >
      If the description is empty or unintelligible, set category to Other,
      priority to Standard, reason to "Description is empty or unintelligible",
      and flag to NEEDS_REVIEW. Never hallucinate a category or invent details
      not present in the input.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: >
      File path to an input CSV (e.g., ../data/city-test-files/test_pune.csv)
      containing complaint rows with description text. The category and
      priority_flag columns are stripped and must be regenerated.
    output: >
      File path to an output CSV (e.g., uc-0a/results_pune.csv) containing
      all original columns plus the four classification fields: category,
      priority, reason, and flag — one row per complaint, preserving input
      row order.
    error_handling: >
      If a row fails classification (e.g., malformed data), log the row index
      and error, set that row's output to category: Other, priority: Standard,
      reason: "Classification failed — see logs", flag: NEEDS_REVIEW, and
      continue processing remaining rows. Never skip rows silently or halt
      the batch on a single-row failure.
