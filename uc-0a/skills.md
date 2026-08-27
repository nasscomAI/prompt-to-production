skills:
  - name: classify_complaint
    description: Takes one citizen complaint row and determines Category, Priority, Reason, and Flag.
    input: A single row of text from the citizen complaint description.
    output: A dictionary containing Category, Priority, Reason, and Flag.
    error_handling: If the text is empty, set category to Other and flag as NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV and applies the classification logic to every row.
    input: A CSV file located at ../data/city-test-files/test_pune.csv
    output: A processed CSV file named results_pune.csv.
    error_handling: Skip rows that are completely blank or corrupted.