skills:

  - name: classify_complaint
    description: Classifies one citizen complaint into an allowed category and priority, provides an evidence-based reason, and flags genuine category ambiguity for review.
    input: One complaint record containing complaint text, provided as a structured complaint row or complaint description string.
    output: A classification record containing exactly category, priority, reason, and flag.
    error_handling: If the complaint is missing or insufficient, return category Other, priority Low, and flag NEEDS_REVIEW without inventing details; if the category is genuinely ambiguous, select the best-supported allowed category and set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads complaint records from an input CSV, applies classify_complaint independently to each row, and writes the classification results to an output CSV.
    input: A CSV file containing complaint records, including a description field for each complaint.
    output: A CSV file containing the original complaint identifier and required classification fields category, priority, reason, and flag for each input row.
    error_handling: Process each row independently, preserve valid rows when possible, and report invalid or missing input data without inventing complaint information; ambiguous classifications must use the NEEDS_REVIEW flag.