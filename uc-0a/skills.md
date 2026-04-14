# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: >
      A single row (dict / named tuple) containing at minimum a `description`
      field with the raw complaint text.
    output: >
      A dict with four keys:
        - category (str): Exactly one of Pothole, Flooding, Streetlight, Waste,
          Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        - priority (str): One of Urgent, Standard, Low.
          Urgent is mandatory when any severity keyword is present
          (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse).
        - reason (str): One sentence citing specific words from the description
          that justify the chosen category and priority.
        - flag (str): "NEEDS_REVIEW" if the category is genuinely ambiguous,
          blank ("") otherwise.
    error_handling: >
      If the description is empty or unintelligible, set category to "Other",
      priority to "Low", reason to "Description is empty or unintelligible",
      and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: >
      Two file paths:
        - input_path (str): Path to a CSV file with at least a `description`
          column (category and priority_flag columns are stripped).
        - output_path (str): Path where the classified results CSV will be written.
    output: >
      A CSV file at output_path containing all original columns plus the four
      classification columns (category, priority, reason, flag) appended to
      each row. Returns the count of rows processed and any rows flagged
      NEEDS_REVIEW.
    error_handling: >
      If the input file is missing or unreadable, raise a clear error with the
      file path. If any individual row fails classification, log the row number
      and error, set that row's flag to "NEEDS_REVIEW", and continue processing
      the remaining rows.
