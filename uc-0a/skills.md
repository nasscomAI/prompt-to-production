# skills.md

skills:
  - name: classify_complaint
    description: >
      Analyzes a single citizen complaint to determine its category and priority. 
      Strict taxonomy enforcement: MUST be one of {Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other}.
      Priority logic: Set to 'Urgent' if description contains severity keywords: {injury, child, school, hospital, ambulance, fire, hazard, fell, collapse}. Otherwise assigns 'Standard' or 'Low'.
    input: Object containing 'description' (string) field.
    output: 
      category: "Selected exact string from taxonomy list."
      priority: "Priority level: Urgent, Standard, or Low."
      reason: "One sentence citing specific words from description."
      flag: "NEEDS_REVIEW (if ambiguous) or blank."
    error_handling: >
      Assign category 'Other' and set flag 'NEEDS_REVIEW' if the input description is empty, 
      nonsense, or does not clearly fit a defined category.

  - name: batch_classify
    description: >
      Orchestrates the classification of multiple complaints from a CSV source. 
      Reads from '../data/city-test-files/test_[city].csv' where 'category' and 'priority_flag' columns are stripped. 
      Applies 'classify_complaint' logic and writes results to 'uc-0a/results_[city].csv'.
    input: String path to the input CSV file.
    output: String path to the generated results CSV file.
    error_handling: >
      Row-level failures (e.g., specific malformed entries) are logged but do not halt the batch. 
      File-level errors (missing file paths) will abort with a descriptive error.
