# skills.md

skills:
  - name: classify_complaint
    description: Categorizes and prioritizes a single complaint row based on the description and defined severity keywords.
    input: A single complaint record containing a 'description' string.
    output: >
      A classified object with 'category' (Pothole, Flooding, etc.), 'priority' (Urgent, Standard, Low), 
      'reason' (one-sentence citation), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: >
      If the description is ambiguous, set category to 'Other' and flag to 'NEEDS_REVIEW'. 
      If priority is unclear and no keywords are present, default to 'Standard'.

  - name: batch_classify
    description: Processes an entire CSV file of complaints, applying classify_complaint to each row and generating a results CSV.
    input: Path to an input CSV file (e.g., test_[city].csv).
    output: Path to the generated output CSV file (e.g., results_[city].csv).
    error_handling: >
      Skips malformed rows and logs them, ensuring the output file is still generated for all successfully 
      processed rows.
