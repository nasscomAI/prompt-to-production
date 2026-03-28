# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Evaluates a single citizen complaint description, referencing predefined categories and severity keywords to generate a classification.
    input: A single unclassified complaint record containing the description text.
    output: A record containing the fields 'category', 'priority', 'reason' (one sentence citing exact words), and 'flag'.
    error_handling: If the complaint text is ambiguous, output category as 'Other' and assign 'NEEDS_REVIEW' to the flag field without exhibiting false confidence.

  - name: batch_classify
    description: Orchestrates the processing of an entire input CSV by applying classify_complaint to each row and writing the updated rows to an output CSV.
    input: File path to the input CSV (e.g., `../data/city-test-files/test_[your-city].csv`).
    output: File path to the output CSV (e.g., `uc-0a/results_[your-city].csv`).
    error_handling: Log any unreadable rows, append skip-flags where necessary to ensure no row stops the batch execution, and safely flush valid classifications to the output.
