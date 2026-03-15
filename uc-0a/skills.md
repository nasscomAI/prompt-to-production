skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to assign a category, priority level, extraction reason, and review flag.
    input: String containing a single complaint row (specifically the description text).
    output: Object containing category, priority, reason, and flag.
    error_handling: If the complaint does not fit clearly into a predefined category or is ambiguous, assign category "Other" and set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of complaints, processes each row using classify_complaint, and writes the results to an output CSV.
    input: File path to the input CSV containing complaints (e.g., test_[city].csv).
    output: File path to the generated output CSV (e.g., results_[city].csv). The output file explicitly includes the newly classified columns (`category`, `priority`, `reason`, `flag`) alongside the original input columns (like `complaint_id`).
    error_handling: If a row is malformed or classification fails, log the error with the row ID and continue to the next row.
