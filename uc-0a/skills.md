# skills.md

skills:
  - name: classify_complaint
    description: Analyzes one citizen complaint row and classifies its category, priority, reason, and flag.
    input: A dictionary or string representing a single complaint row text.
    output: A dictionary containing 'category', 'priority', 'reason', and 'flag'.
    example_output: >
      {
        "category": "Pothole",
        "priority": "Urgent",
        "reason": "Complaint categorized based on 'pothole' and marked urgent due to 'child'.",
        "flag": ""
      }
    error_handling: If the input is invalid or ambiguous, classifiy as 'Other' category, 'Standard' or 'Low' priority, and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: Two strings representing the input CSV file path and the output CSV file path.
    output: Creates/writes an output CSV file on disk.
    example_output: >
      A CSV file identically structured to the input, but with four appended columns: 'category', 'priority', 'reason', and 'flag'.
      Example command execution:
      python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
    error_handling: Flags nulls, does not crash on bad rows, and ensures it continues processing and produces an output file even if some specific rows fail processing.

    example of the final command:
    python classifier.py \
  --input ../data/city-test-files/test_pune.csv \
  --output results_pune.csv

