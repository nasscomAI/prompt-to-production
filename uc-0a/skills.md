# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category and priority, providing a justification reason and an ambiguity flag.
    input: A complaint description string or a data row containing a description.
    output: A structured object containing category (string), priority (string), reason (string), and flag (string).
    error_handling: If the description is ambiguous, set flag to 'NEEDS_REVIEW' and category to 'Other'.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes the results to a new CSV file.
    input: Path to an input CSV file containing complaint descriptions.
    output: Path to an output CSV file containing the classification results.
    error_handling: Handle file access errors and log individual row failures while continuing the batch process.
