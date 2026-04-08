# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority level, reason, and review flag.
    input: >
      A single complaint row (dictionary/object) containing at minimum a
      `description` field with free-text citizen complaint text.
    output: >
      A dictionary/object with four fields:
        - category (string): Exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        - priority (string): One of Urgent, Standard, Low. Must be Urgent if description contains any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse).
        - reason (string): One sentence citing specific words from the description that justify the category and priority.
        - flag (string): NEEDS_REVIEW if the complaint is genuinely ambiguous; blank otherwise.
    error_handling: >
      If the description is empty or missing, set category to Other, priority to
      Low, reason to "No description provided", and flag to NEEDS_REVIEW. If the
      description does not clearly map to a single category, assign the best-fit
      category (or Other) and set flag to NEEDS_REVIEW. Never hallucinate a
      confident classification for ambiguous input.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the classified results to an output CSV file.
    input: >
      Two file paths:
        - input_path (string): Path to a CSV file containing complaint rows with a `description` column. The `category` and `priority_flag` columns are stripped.
        - output_path (string): Path where the output CSV will be written.
    output: >
      A CSV file at output_path containing all original columns plus four new
      columns: category, priority, reason, flag. Row order is preserved. The
      number of output rows must exactly match the number of input rows.
    error_handling: >
      If the input file does not exist or is not a valid CSV, raise an error with
      a descriptive message. If any individual row fails classification, log the
      error, set that row's flag to NEEDS_REVIEW with reason "Classification
      failed — manual review required", and continue processing remaining rows.
      Never silently drop or duplicate rows.
