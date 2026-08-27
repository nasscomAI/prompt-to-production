# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint and returns its category, priority, reason, and review flag.
    input: A dictionary containing the complaint description and ID.
    output: A dictionary with keys: category, priority, reason, flag.
    error_handling: If the description is empty or unreadable, returns category: Other, priority: Low, reason: "Empty description", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Processes a CSV file of complaints, applying classification to each row and saving the results.
    input: Path to the input CSV file and path for the output CSV file.
    output: A CSV file containing the original data plus the classified fields.
    error_handling: Skips malformed rows and logs them, ensuring the process continues for remaining valid rows.
