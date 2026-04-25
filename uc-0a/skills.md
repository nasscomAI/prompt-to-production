# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category and priority, citing evidence from the description.
    input: dict (row containing 'complaint_id' and 'description')
    output: dict (keys: 'complaint_id', 'category', 'priority', 'reason', 'flag')
    error_handling: For empty descriptions or missing fields, output 'Other' category and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the classification process for a full CSV file, ensuring robust error handling per row.
    input: input_path (str), output_path (str)
    output: Writes results to output_path CSV file.
    error_handling: Must not crash on individual row failures; flags nulls and produces partial output if necessary.
