# skills.md

skills:

  - name: classify_complaint

    description: Classifies one citizen complaint into an allowed category and priority, provides a one-sentence reason using words from the description, and flags genuine ambiguity for review.

    input: One complaint row as a dictionary containing a complaint description and complaint_id.

    output: A dictionary containing complaint_id, category, priority, reason, and flag.

    error_handling: If the complaint description is missing or invalid, return category Other, priority Standard, a one-sentence reason stating that the description is missing or invalid, and flag NEEDS_REVIEW. If the category is genuinely ambiguous or cannot be determined from the description, return category Other and flag NEEDS_REVIEW.

  - name: batch_classify

    description: Reads a complaint CSV, classifies each row using classify_complaint, and writes the classification results to an output CSV.

    input: Input CSV file path containing complaint rows and output CSV file path.

    output: CSV file containing complaint_id, category, priority, reason, and flag for every input row.

    error_handling: Handle missing or malformed rows without crashing, flag invalid rows for review, and continue processing remaining rows so an output CSV is produced.