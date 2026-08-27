# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: A single civic complaint row containing a description.
    output: A dictionary/object with fields category, priority, reason, and flag.
    error_handling: Return category as Other, priority as Standard or Low, set flag as NEEDS_REVIEW, and provide the reason noting the ambiguity.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File path to the input CSV and output CSV.
    output: Generates a new CSV file containing the original rows appended with their classification data.
    error_handling: Log errors for invalid rows and continue processing the remaining rows securely.
