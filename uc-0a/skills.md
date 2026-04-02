# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category, priority level, reason, and review flag.
    input: >
      A single complaint row (dictionary/object) containing at minimum a
      `description` field (string) with the citizen's complaint text.
    output: >
      A dictionary/object with exactly four fields:
        - category (string): One of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        - priority (string): One of Urgent, Standard, Low.
        - reason (string): One sentence citing specific words from the description.
        - flag (string): "NEEDS_REVIEW" if category is ambiguous or Other; blank otherwise.
    error_handling: >
      If the description is empty, null, or not a recognizable civic complaint,
      return category: Other, priority: Low, reason: "Description is empty or
      not a valid civic complaint.", flag: NEEDS_REVIEW.


  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: >
      File path to an input CSV containing complaint rows. Each row must have
      a `description` column. Optional columns (e.g., complaint_id, location)
      are passed through to the output unchanged.
    output: >
      File path to the output CSV. Each row contains all original columns plus
      the four classification fields: category, priority, reason, flag.
    error_handling: >
      If the input file is missing or unreadable, raise a clear error with the
      file path. If individual rows fail classification, write them to the output
      with category: Other, priority: Low, flag: NEEDS_REVIEW, and reason
      describing the failure — do not skip or silently drop rows.
