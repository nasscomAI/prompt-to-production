skills:
  - name: classify_complaint
    description: Classifies a single complaint to determine category, priority, reasoned justification, and ambiguity flagging.
    input: A single complaint row (description text).
    output: category, priority, reason, and flag out.
    error_handling: If the complaint description is incomplete or ambiguous, the outcome still populates the nearest category and sets the flag to NEEDS_REVIEW to avoid false confidence.

  - name: batch_classify
    description: Sequentially reads an input CSV of complaints, applies classify_complaint per row, and reliably writes the results to an output CSV.
    input: Filepath to the input CSV file (e.g., ../data/city-test-files/test_[your-city].csv).
    output: Outputs a written CSV with populated classification columns (e.g., uc-0a/results_[your-city].csv).
    error_handling: Handles input rows missing standard formats gracefully by leaving fields blank or marking as NEEDS_REVIEW so processing of the batch file completes without crashing.
