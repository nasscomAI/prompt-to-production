# skills.md — UC-0A Complaint Classifier

Based on @README.md

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into category, priority, reason,
      and flag according to the UC-0A schema.
    input: >
      A single complaint record as a dict with at minimum a "description" string
      field containing the raw complaint text.
    output: >
      A dict with four fields — category (str, one of the 10 allowed values:
      Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
      Heat Hazard, Drain Blockage, Other), priority (str: Urgent | Standard | Low),
      reason (str, one sentence citing words from the description), flag (str:
      NEEDS_REVIEW or empty string).
    error_handling: >
      If description is missing or empty, return category: Other, priority: Low,
      reason: "Description field is empty — cannot classify.", flag: NEEDS_REVIEW.
      If the description does not map clearly to any allowed category, return
      category: Other and flag: NEEDS_REVIEW rather than guessing.
      Must check for severity keywords (injury, child, school, hospital,
      ambulance, fire, hazard, fell, collapse) to set priority to Urgent.

  - name: batch_classify
    description: >
      Reads an input CSV of complaint rows, applies classify_complaint to each
      row, and writes the results with the four classification fields to an output
      CSV.
    input: >
      File path to a CSV file (str) containing at minimum a "description" column;
      the category and priority_flag columns may be absent or stripped.
      Expected input path: ../data/city-test-files/test_[your-city].csv
    output: >
      A CSV file written to the specified output path, containing all original
      columns plus category, priority, reason, and flag columns for every row.
      Expected output path: uc-0a/results_[your-city].csv
    error_handling: >
      If the input file is not found or cannot be parsed as CSV, raise a
      FileNotFoundError or ValueError with a descriptive message and halt — do
      not write a partial output file. Rows where classify_complaint returns
      NEEDS_REVIEW are written normally and must not be skipped or filtered.
      Must verify all category values match the exact allowed list and all
      priority values are one of Urgent, Standard, or Low.
