# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.
skills:
  - name: classify_complaint
    description: Analyzes a single dictionary representing a complaint row and returns a classification object based on RICE enforcement rules.
    input: dict (CSV row with keys like 'description', 'complaint_id')
    output: dict (keys: complaint_id, category, priority, reason, flag)
    error_handling: Returns a default classification with flag 'NEEDS_REVIEW' and category 'Other' if input is malformed or description is too short.

  - name: batch_classify
    description: Reads a CSV file, iterates through rows, applies classify_complaint per row, and writes the results to a new CSV.
    input file: `../data/city-test-files/test_[city].csv`
    output file: `results_[city].csv`
    error_handling: Logs an error if a row fails; skips empty rows and ensures the output file is created even if some rows are skipped.