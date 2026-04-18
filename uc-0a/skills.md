# skills.md
skills:
  - name: classify_complaint
    description: Classifies a single raw citizen complaint description by assigning an exact category, determining priority based on specific severity keywords, and generating a text-cited reason.
    input: A single raw complaint text description (string).
    output: A structured object containing category, priority, reason (one sentence), and flag.
    rules:
      - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Exact strings only — no variations."
      - "Priority must be Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
      - "The reason field must be exactly one sentence and cite specific words from the description."
      - "If the category is genuinely ambiguous, set flag to NEEDS_REVIEW."
    error_handling: If the complaint is genuinely ambiguous, set the flag to "NEEDS_REVIEW" and avoid confidently guessing.

  - name: batch_classify
    description: Reads complaints from an input CSV, evaluates each row using classify_complaint, and writes all results to an output CSV.
    input: Filepath to the input CSV file containing complaint rows.
    output: Filepath to the generated output CSV file containing the classified rows.
    error_handling: If the file is missing or malformed, raise an IO error. If an individual row fails processing, log the error and continue to the next row.
