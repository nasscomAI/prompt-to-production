# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: "classify_complaint"
    description: "Transforms a raw civic complaint into a structured classification following strict taxonomy and severity rules."
    input: "Dictionary containing 'complaint_id' and 'description'."
    output: "Dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'."
    error_handling: "If input is missing 'description', return category 'Other' and flag 'NEEDS_REVIEW'."

  - name: "batch_classify"
    description: "Orchestrates the processing of a CSV file of complaints, applying classification to each row and saving results to a new CSV."
    input: "Paths for input_csv and output_csv."
    output: "A summary message indicating success or detailing rows that failed."
    error_handling: "Must log errors for malformed CSV rows but continue processing the rest of the file."
