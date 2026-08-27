skills:
  - name: classify_complaint
    description: Evaluates a single citizen complaint row's description to determine its exact civic category (Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other) and assigns a priority level (Urgent/Standard/Low) based on severity keywords.
    input: A single raw complaint row containing a description field. Excludes metadata, user profile data, and historical classification data.
    output: A structured object containing the exact keys `category` (exact allowed strings only), `priority` (Urgent if injury/child/school/hospital/ambulance/fire/hazard/fell/collapse present, otherwise Standard or Low), `reason` (one sentence citing specific words from description), and `flag` (NEEDS_REVIEW or blank).
    error_handling: If the description is null/empty, or if the category is genuinely ambiguous and cannot be definitively categorized, it sets `category` to "Other" and `flag` to "NEEDS_REVIEW".

  - name: batch_classify
    description: Iterates over an input CSV dataset to classify citizen complaints in bulk, applying the `classify_complaint` skill per row.
    input: A string path pointing to a valid input CSV file containing multiple complaint rows (e.g., ../data/city-test-files/test_[your-city].csv).
    output: A string path pointing to the target written CSV file populated with all verified columns, including complaint_id, category, priority, reason, and flag (e.g., uc-0a/results_[your-city].csv).
    error_handling: Gracefully flags null/empty rows with category "Other" and flag "NEEDS_REVIEW", and will not crash the batch execution if a bad row is encountered.
