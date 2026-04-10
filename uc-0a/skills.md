skills:
  - name: classify_complaint
    description: Classifies one complaint row into allowed category, priority, reason, and review flag.
    input: "dict with complaint_id:string and description:string from one CSV row"
    output: "dict with complaint_id:string, category:enum, priority:enum, reason:string, flag:string|blank"
    error_handling: "If description is blank, malformed, or ambiguous across categories, return category=Other, priority=Standard, and flag=NEEDS_REVIEW with explanatory reason."

  - name: batch_classify
    description: Reads input complaint CSV, applies classify_complaint row-by-row, and writes output CSV safely.
    input: "input_path:string to CSV with complaint rows; output_path:string for results CSV"
    output: "CSV file with columns complaint_id,category,priority,reason,flag for every input row"
    error_handling: "Handles null fields and row-level errors without crashing; writes fallback row with NEEDS_REVIEW for failed records."
