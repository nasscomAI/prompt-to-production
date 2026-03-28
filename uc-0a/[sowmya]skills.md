skills:
  - name: classify_complaint
    description: Classifies one raw citizen complaint row into exact category, priority, reason, and flag fields.
    input: dictionary (representing a single complaint row with description text)
    output: dictionary (containing category, priority, reason, and flag strings)
    error_handling: Return category as 'Other' and flag as 'NEEDS_REVIEW' if ambiguity is present, and refuse to guess sub-categories or assign confident categorization to unintelligible inputs.
  - name: batch_classify
    description: Iterates through the input CSV file to apply classify_complaint to each row and writes the structured output CSV.
    input: file paths (string paths for the input CSV and output CSV)
    output: CSV file (written output containing processed rows)
    error_handling: Stop execution if input file is missing, and prevent crashes by gracefully handling individual bad rows.