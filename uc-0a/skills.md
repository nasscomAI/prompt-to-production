# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Takes a single complaint description and returns a classified row with category, priority, reason, and flag — enforcing the allowed taxonomy, severity keyword rules, and NEEDS_REVIEW logic from agents.md.
    input: >
      A plain-text string — the complaint description from one CSV row.
      No additional context (prior rows, city name, complainant identity) is passed.
    output: >
      A dict with four fields:
        category  — exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
                    Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        priority  — one of: Urgent, Standard, Low
        reason    — one sentence quoting or directly referencing specific words
                    from the input description
        flag      — "NEEDS_REVIEW" if category is ambiguous, otherwise blank string
    error_handling: >
      If the description is empty or whitespace-only, return category: Other,
      priority: Low, reason: "Description was empty — cannot classify.",
      flag: NEEDS_REVIEW.
      If severity keywords (injury, child, school, hospital, ambulance, fire,
      hazard, fell, collapse) are present, priority must be Urgent regardless
      of any other signal.
      If the category cannot be determined with confidence, return category: Other
      and flag: NEEDS_REVIEW — never invent a specific category.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with the original fields plus the four classification columns appended.
    input: >
      Two file paths (strings):
        input_path  — path to the source CSV; must contain at minimum a
                      "description" column; other columns are passed through unchanged
        output_path — path where the results CSV will be written
    output: >
      A results CSV at output_path containing all original columns plus:
        category, priority, reason, flag
      One row per input row, in the same order.
      On completion, prints a summary: total rows processed, Urgent count,
      NEEDS_REVIEW count.
    error_handling: >
      If input_path does not exist, raise FileNotFoundError with a clear message.
      If the "description" column is missing from the CSV, raise ValueError
      listing the columns that were found.
      If any individual row fails classify_complaint, write category: Other,
      priority: Low, reason: "Classification error — see flag.", flag: NEEDS_REVIEW
      for that row and continue processing remaining rows.
      Never silently skip a row or halt mid-batch.
