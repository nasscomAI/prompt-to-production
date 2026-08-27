Skill 1: classify_complaint
Description: Classifies a single complaint row into category, priority, reason, and flag.
Input: Dictionary with complaint fields (including description).
Output: Dictionary with keys: category, priority, reason, flag.
Error handling: If input is missing or ambiguous, returns category: Other and flag: NEEDS_REVIEW.
Skill 2: batch_classify
Description: Reads input CSV, applies classify_complaint to each row, writes output CSV.
Input: Input CSV path, output CSV path.
Output: CSV file with classified rows.
Error handling: Flags nulls, does not crash on bad rows, produces output even if some rows fail.
