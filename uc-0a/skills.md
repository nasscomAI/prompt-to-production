# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category, priority, reason, and review flag.
    input: >
      A single complaint row containing at minimum a text description field.
      May also include metadata such as complaint_id, date, and location.
    output: >
      A dictionary/row with exactly four fields:
        category — one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        priority — one of: Urgent, Standard, Low. Must be Urgent if description contains any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse).
        reason — one sentence citing specific words from the complaint description that justify the category and priority.
        flag — NEEDS_REVIEW if the category is genuinely ambiguous, otherwise blank.
    error_handling: >
      If the description is empty or unintelligible, set category to Other,
      priority to Low, reason to "Description not classifiable", and flag to NEEDS_REVIEW.
      If the description matches multiple categories with no clear winner,
      assign the best-fit category and set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: >
      File path to a CSV file with at least a description column.
      Expects the format from ../data/city-test-files/test_[city].csv (15 rows, category and priority_flag columns stripped).
    output: >
      A CSV file at the specified output path containing all original columns
      plus four new columns: category, priority, reason, flag.
      One output row per input row, in the same order.
    error_handling: >
      If the input file does not exist or cannot be read, exit with a clear error message.
      If a single row fails classification, log a warning for that row,
      set its output to category: Other, priority: Low, reason: "Classification failed", flag: NEEDS_REVIEW,
      and continue processing the remaining rows.
