# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
## Skill 1
  
name: classify_ complaint

description: Classifies a single citizen complaint according to the UC-0A classification rules.

input: A complaint row containing complaint_id and description.

output: A classification containing complaint_id, category, priority, reason, and flag.

error_handling: If the complaint is ambiguous or cannot be confidently classified, use category Other and set the flag to NEEDS_REVIEW. Do not invent categories or sub-categories.

## Skill 2

name: batch_classify

description: Processes all complaints from the input CSV and generates the required classification output CSV.

input: Input CSV file containing complaint records.

output: Output CSV containing complaint_ id, category, priority, reason, and flag for every complaint.

error_ handling: Continue processing remaining rows if one row causes an error, and ensure the output contains a result for every input complaint.
  
