# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag according to the predefined schema.
    input: A string containing the complaint description text.
    output: A dictionary/object with keys 'category', 'priority', 'reason', 'flag' where category is exact string from allowed values, priority is Urgent/Standard/Low, reason is one sentence citing specific words, flag is NEEDS_REVIEW or blank.
    error_handling: If category cannot be determined unambiguously, sets category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row's description, and writes the results to an output CSV file.
    input: File path to input CSV containing complaint descriptions (string).
    output: Writes output CSV file with columns category, priority, reason, flag for each row.
    error_handling: For rows where classification fails or is ambiguous, applies the error handling from classify_complaint skill.
