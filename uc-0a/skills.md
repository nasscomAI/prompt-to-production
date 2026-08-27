# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row by assigning category, priority, reason, and flag based on complaint description text.
    input: Dict with keys complaint_id and description. Format {"complaint_id": "string", "description": "string"}.
    output: Dict with keys complaint_id, category, priority, reason, flag. Format {"complaint_id": "...", "category": "one of 10 categories or Other", "priority": "Urgent|Standard|Low", "reason": "one sentence", "flag": "NEEDS_REVIEW or empty"}.
    error_handling: If description is empty/None return category=Other, priority=Standard, reason="No description provided", flag=NEEDS_REVIEW. If description < 3 chars treat as missing. Never raise exception; always return valid dict.

  - name: batch_classify
    description: Reads input CSV with complaint data, applies classify_complaint to each row, writes results to output CSV.
    input: CSV file path with columns complaint_id and description. Expected 15 rows per city, handles any count.
    output: CSV file written to disk with columns complaint_id, category, priority, reason, flag. One row per input complaint, no missing values, all rows have all 5 columns.
    error_handling: If input file not found print error and exit code 1. If CSV malformed skip rows and log row number. If classify_complaint fails catch and set category=Other, flag=NEEDS_REVIEW, continue. Always write output file even if some rows fail. Print summary of rows processed and flagged.
