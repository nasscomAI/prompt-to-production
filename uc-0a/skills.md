# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row and returns category, priority, reason, and ambiguity flag.
    input: "Single complaint record: {description: str}. Description may be 1–500 words describing a city infrastructure or service complaint."
    output: "Classification result: {category: str, priority: str, reason: str, flag: str}. Category is one of 10 allowed values. Priority is Urgent|Standard|Low. Reason is one sentence citing specific complaint text. Flag is NEEDS_REVIEW (if ambiguous) or empty string."
    error_handling: "If description is empty or null, return category: Other, priority: Standard, reason: 'Cannot classify empty complaint', flag: NEEDS_REVIEW. If description contains contradictory categories, set flag: NEEDS_REVIEW and category: Other. If input is not a string, raise ValueError."

  - name: batch_classify
    description: Reads a CSV file, applies classify_complaint to each row, appends results, and writes output CSV.
    input: "Input CSV path (string): file must contain 'description' column. Output CSV path (string): destination file path."
    output: "Output CSV with all original columns plus four new columns: category, priority, reason, flag. One row per input complaint (no filtering or dropping)."
    error_handling: "If input file missing, raise FileNotFoundError with path. If 'description' column is missing, raise ValueError. If output path is not writable, raise PermissionError. If any row fails classify_complaint, log warning and set category: Other, flag: NEEDS_REVIEW, reason: 'Classification error.'"
