# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a standardized category, priority level, textual justification, and ambiguity flag based on strict enforcement rules.
    input: Dictionary containing complaint row data with `complaint_id` (str) and complaint description text (str).
    output: Dictionary containing `complaint_id` (str), `category` (one of 10 allowed exact strings), `priority` (Urgent, Standard, or Low), `reason` (single sentence citing description words), and `flag` (NEEDS_REVIEW or blank).
    error_handling: If the complaint category is ambiguous or cannot be determined from description alone, set category to "Other" and flag to "NEEDS_REVIEW". If the description is missing or null, assign priority "Standard", reason "Description missing or invalid.", category "Other", and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, executes `classify_complaint` for each row, and writes the structured results to a target output CSV file.
    input: `input_path` (str, path to input CSV file) and `output_path` (str, path to write output CSV file).
    output: CSV file created at `output_path` containing columns `complaint_id`, `category`, `priority`, `reason`, and `flag`.
    error_handling: Flags missing or null values, handles malformed CSV rows gracefully without crashing the process, and ensures an output file is generated even if individual rows encounter errors.
