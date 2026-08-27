# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row based on its description into category and priority.
    input: A dictionary representing a single row from the complaint CSV.
    output: A dictionary containing category, priority, reason, and flag.
    error_handling: If the description is missing or empty, return category: Other, priority: Standard, flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Processes an entire CSV file of complaints and writes the results to an output CSV.
    input: Path to an input CSV file and path to an output CSV file.
    output: Writes a CSV file with the classification results.
    error_handling: Flags null rows and skips rows that cause unexpected errors, ensuring the process continues.
