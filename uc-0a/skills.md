# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category, priority, and reason based on a text description.
    input: A string containing the complaint description.
    output: A dictionary containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: Returns 'Other' category and 'NEEDS_REVIEW' flag if the description is ambiguous or empty.

  - name: batch_classify
    description: Processes an entire CSV file of complaints, classifying each row and writing the results to a new CSV file.
    input: Path to an input CSV file containing raw complaint descriptions.
    output: Path to an output CSV file containing the original descriptions plus classification columns.
    error_handling: Skips malformed rows and logs them, ensuring the process completes for all valid entries.
