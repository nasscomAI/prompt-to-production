# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category and priority level with a cited reason.
    input: One CSV row containing a complaint description (string).
    output: A record with four fields — category (one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent, Standard, or Low), reason (one sentence citing specific words from the description), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or too vague to determine a category, set category to Other, priority to Low, and flag to NEEDS_REVIEW with a reason stating insufficient information.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: A CSV file path with a description column (category and priority_flag columns stripped). Accepts optional --input and --output CLI arguments.
    output: A CSV file with the original columns plus category, priority, reason, and flag columns populated for every row.
    error_handling: If a row fails to parse or the description column is missing, skip the row, log a warning, and continue processing remaining rows. Exit with a non-zero code if the input file cannot be read.
