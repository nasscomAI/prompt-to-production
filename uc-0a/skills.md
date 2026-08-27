skills:
  - name: classify_complaint
    description: Transforms a city-specific (Pune, Ahmedabad, Hyderabad, or Kolkata) complaint description into a structured classification based on RICE taxonomy, with specialized detection for local hazards and safety priorities.
    input: A data dictionary containing 'description' and 'complaint_id'.
    output: A dictionary with 'category', 'priority', 'reason', and 'flag'.
    error_handling: Defaults to 'Other' and 'NEEDS_REVIEW' for ambiguous descriptions.

  - name: batch_classify
    description: Orchestrates the end-to-end processing of any city test file (e.g., test_[city].csv), persisting results to a corresponding results_[city].csv.
    input: File paths for a target input CSV and the output destination.
    output: A results_[city].csv file.
    error_handling: Resilient to missing fields and malformed rows.
