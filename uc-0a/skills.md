skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint text into predefined categories, assigns priority, provides a reason, and flags ambiguity.
    input: String containing the text description of the complaint.
    output: A verifiable classification containing four fields - category (from predefined list), priority (Urgent/Standard/Low), reason (one sentence), and flag (NEEDS_REVIEW or blank).
    error_handling: If the category is genuinely ambiguous or cannot be determined from the description alone, sets the flag field to NEEDS_REVIEW.

  - name: batch_classify
    description: Runs the classifier.py script to read an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Command line arguments for input and output file paths (e.g., --input ../data/city-test-files/test_pune.csv --output results_pune.csv).
    output: A new CSV file containing the original rows with the appended classification fields (category, priority, reason, flag).
    error_handling: Handles missing or malformed rows by skipping them or logging an error, and ensures the output file is safely written even if some rows fail.
