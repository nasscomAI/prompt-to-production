skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a strict schema containing category, priority, reason, and an ambiguity flag.
    input:
      type: object
      format: A single mapped row from the input CSV containing the complaint description.
    output:
      type: object
      format: Contains 'category' (exact predefined string), 'priority' (Urgent, Standard, or Low), 'reason' (exactly one sentence citing description words), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: Prevents taxonomy drift and hallucinated sub-categories by strictly enforcing the allowed category list; avoids severity blindness by forcing 'Urgent' if severity keywords exist; prevents missing justification by rejecting output if the reason lacks exact word citations; avoids false confidence by setting the flag to 'NEEDS_REVIEW' when the complaint is genuinely ambiguous rather than guessing.
  - name: batch_classify
    description: Reads an entire input CSV of complaints, applies the classify_complaint skill row-by-row, and writes the aggregated results to an output CSV.
    input:
      type: file_path
      format: Path to the input CSV file containing up to 15 complaint rows with stripped category and priority_flag columns.
    output:
      type: file_path
      format: Path to the generated output CSV file containing the classifications.
    error_handling: Handles invalid or malformed CSV inputs by halting with a read error; if an individual row fails the strict classification taxonomy or validation requirements, it sets the row flag to 'NEEDS_REVIEW' and logs the failure rather than halting the entire batch, ensuring all rows are processed successfully.
