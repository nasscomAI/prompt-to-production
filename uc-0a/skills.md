# skills.md

skills:
  - name: classify_complaint
    description: Classifies a citizen report into the municipal taxonomy and calculates priority based on the safety keywords defined in agents.md.
    input: String containing the complaint description.
    output: A structured object containing category (exact taxonomy match), priority (Urgent/Standard/Low), reason (one sentence with citation), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is ambiguous or missing key details, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Coordinates the end-to-end processing of a CSV file, applying classify_complaint to each row and saving the results.
    input: File path to the input CSV (e.g., ../data/city-test-files/test_pune.csv).
    output: File path to the results CSV containing classification columns (e.g., results_pune.csv).
    error_handling: Log errors for failed rows and continue processing; abort only on fatal file I/O errors.
