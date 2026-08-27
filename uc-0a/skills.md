# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint by category, priority, reason, and ambiguity flag using the enforced taxonomy and severity keyword rules.
    input: A single complaint row containing at minimum a text description field (string).
    output: A dictionary/row with four fields — category (one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent, Standard, or Low), reason (one sentence citing specific words from the description), and flag (NEEDS_REVIEW if ambiguous, blank otherwise).
    error_handling: If the description is empty or missing, set category to Other, priority to Low, reason to "No description provided", and flag to NEEDS_REVIEW. If the description does not clearly map to a single category, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: File path to an input CSV containing complaint rows with a text description column, and a file path for the output CSV.
    output: A CSV file at the specified output path with all original columns preserved plus the four classification fields (category, priority, reason, flag) — one row per input row, no rows added or dropped.
    error_handling: If the input file is missing or unreadable, exit with a clear error message. If any individual row fails classification, log the row number and apply the empty-description fallback (category Other, priority Low, flag NEEDS_REVIEW) so that the batch continues without crashing.
