# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
Input: one complaint row  
Output: category, priority, reason, flag

Rules:
- Use exact allowed category names.
- Set Urgent if severity keywords appear.
- Give one sentence reason.
- Use NEEDS_REVIEW for ambiguous complaints.

## batch_classify
Input: CSV file  
Output: CSV file with complaint_id, category, priority, reason, flag

Steps:
1. Read input CSV.
2. Apply classify_complaint to each row.
3. Write output CSV.