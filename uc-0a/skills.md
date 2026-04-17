# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority, and justification citing specific keywords.
    input: A raw text string containing the complaint description.
    output: A structured object containing category (exact match from taxonomy), priority (Urgent/Standard/Low), reason (one sentence citation), and flag (NEEDS_REVIEW or blank).
    error_handling: If the category is ambiguous or doesn't fit the schema, output category 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies the classification logic to each row, and writes the results to a specified output CSV.
    input: An input CSV file path and an output CSV file path.
    output: A completed CSV file containing the original descriptions plus the classified category, priority, reason, and flag fields.
    error_handling: Ensures every row in the output file has a valid entry; maps individual classification failures to 'Other' with a 'NEEDS_REVIEW' flag.
