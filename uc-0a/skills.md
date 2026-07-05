# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into a category, assigns priority, provides a reason, and sets a review flag if the category is ambiguous.
    input: A dict representing one CSV row with keys — complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dict with keys — complaint_id, category, priority, reason, flag. category is exactly one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]. priority is one of [Urgent, Standard, Low]. reason is a single sentence citing specific words from the description. flag is "NEEDS_REVIEW" or blank.
    error_handling: If the description is empty or None, set category to "Other", priority to "Low", reason to "No description provided", and flag to "NEEDS_REVIEW". If a row is otherwise malformed, return a result dict with flag "NEEDS_REVIEW" rather than crashing.

  - name: batch_classify
    description: Reads an input CSV of civic complaints, applies classify_complaint to every row, and writes the classified results to an output CSV.
    input: Two file-path strings — input_path (path to test_[city].csv) and output_path (path to write results_[city].csv).
    output: A CSV file at output_path containing all classified rows with columns complaint_id, category, priority, reason, flag.
    error_handling: Skips rows that raise unexpected exceptions (logs a warning to stderr) and continues processing. Always writes the output file even if some rows fail, inserting a NEEDS_REVIEW flag for failed rows. Does not crash on missing optional columns.
