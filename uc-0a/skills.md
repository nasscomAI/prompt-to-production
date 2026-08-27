# skills.md

skills:
  - name: classify_complaint
    description: Categorizes a single citizen complaint text into a strict taxonomy and priority schema.
    input: Text description of a citizen complaint.
    output: Structured data with fields: category, priority, reason, and flag.
    error_handling: Sets the flag to NEEDS_REVIEW if the category is ambiguous; enforces Urgent priority based on severity keywords.

  - name: batch_classify
    description: Processes a CSV file of complaints, applying classify_complaint to each row and writing the results to an output CSV.
    input: Path to an input CSV file containing complaint descriptions.
    output: Path to an output CSV file containing categorized results.
    error_handling: Ensures every processed row includes a citation in the reason field and adheres to strict category/priority lists.

