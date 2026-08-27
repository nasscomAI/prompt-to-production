# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag based on the description text.
    input: A dictionary with complaint fields (id, description, location, date)
    output: A dictionary with keys: category (str), priority (str), reason (str), flag (str)
    error_handling: If description is empty or ambiguous, return category: Other, priority: Standard, reason: "Insufficient information", flag: NEEDS_REVIEW

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes results to an output CSV file.
    input: Path to input CSV file (str), path to output CSV file (str)
    output: Path to the created output CSV file (str)
    error_handling: If input file not found, raise FileNotFoundError. If CSV is malformed, raise ValueError with details.
