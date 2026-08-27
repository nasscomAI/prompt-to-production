# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Takes a single citizen complaint description and classifies it by category and priority, providing a textual reason and setting a flag if ambiguous.
    input: A single string representing the complaint description.
    output: A structured dictionary containing exactly `category`, `priority`, `reason`, and `flag` strings.
    error_handling: If the input is ambiguous or cannot be confidently classified, sets category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes the updated rows to an output CSV file.
    input: Two file paths (strings) - the input CSV file path and the output CSV file path.
    output: Writes a new CSV file to the output path containing the original columns plus the four new classification fields.
    error_handling: If the input file is missing, aborts and raises a FileNotFoundError. If a specific row fails classification, sets its category to "Other", flag to "NEEDS_REVIEW", and continues processing.
