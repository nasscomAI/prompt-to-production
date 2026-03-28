skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row by assigning a category, priority, reason, and flag.
    input: A single citizen complaint record (text description).
    output: String fields for category, priority, reason, and flag.
    error_handling: If the text description is missing, empty, or unreadable, return category Other, priority Low, an appropriate error reason, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File path to the input CSV file.
    output: File path to the generated output CSV file containing classified rows.
    error_handling: If the input file cannot be found or the CSV is malformed, log an error and halt execution.

example of the final command:python classifier.py \
  --input ../data/city-test-files/test_pune.csv \
  --output results_pune.csv

  example of the final output:
  Category,Priority,Reason,Flag
  Pothole,Urgent,"Deep pothole near bus stop. School children at risk during morning hours.",NEEDS_REVIEW
  Flooding,Standard,"Underpass flooded knee-deep after 2hrs rain. Commuters stranded.",NEEDS_REVIEW 