skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint dictionary into a structured dictionary containing category, priority, justification reason, and ambiguity flag.
    input: A dictionary representing a single complaint row with keys including complaint_id, date_raised, city, ward, location, description, reported_by, and days_open.
    output: A dictionary containing exact keys: complaint_id (str), category (str: one of the 10 allowed categories), priority (str: 'Urgent', 'Standard', or 'Low'), reason (str: single sentence citing specific words from description), and flag (str: 'NEEDS_REVIEW' or empty string '').
    error_handling: If description is missing, empty, or unclassifiable due to severe ambiguity, assigns category as 'Other', priority as 'Standard' (or 'Urgent' if severity keywords exist), reason stating data inadequacy, and sets flag to 'NEEDS_REVIEW'. Catches row-level exceptions gracefully without raising unhandled errors.

  - name: batch_classify
    description: Reads an input CSV file containing raw citizen complaints, iterates through each row applying classify_complaint, and writes the structured classification results to an output CSV file.
    input: input_path (str: path to input CSV file, e.g. ../data/city-test-files/test_[city].csv) and output_path (str: path where results CSV will be written, e.g. results_[city].csv).
    output: Writes a CSV file containing columns complaint_id, category, priority, reason, flag for all processed complaints, and returns summary metadata (e.g. total records processed, urgent count, flagged count).
    error_handling: Handles missing input files by logging an error and aborting cleanly; handles empty or malformed rows by writing fallback records with flag 'NEEDS_REVIEW' and category 'Other' to ensure the batch pipeline never crashes and produces output even if individual rows fail.
