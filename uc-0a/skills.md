# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a specific category and priority level based on a strict taxonomy and keyword-triggered urgency.
    input: type: object
format: A dictionary containing the raw complaint description string.
    output: type: object
format: A dictionary containing category (exact string), priority (Urgent/Standard/Low), reason (one sentence with citations), and flag (NEEDS_REVIEW/blank).
    error_handling: If the description is ambiguous or doesn't match a taxonomy category, the skill assigns 'Other' as the category and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an entire CSV file of complaints by applying classification logic to each row and generating a formatted results file.
    input: type: string
format: A file path to a .csv file containing complaint descriptions.
    output: ype: string
format: A file path to the generated .csv output containing the classification results.
    error_handling: If the input file is missing or formatted incorrectly, the skill raises a FileNotFoundError or returns a diagnostic error message and halts processing.
