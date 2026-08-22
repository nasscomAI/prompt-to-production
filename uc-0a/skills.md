# skills.md

skills:
  - name: classify_complaint
    description: Accept complaint_id and description, and classify the complaint.
    input: dict with complaint_id and description
    output: dict with complaint_id, category, priority, reason, flag
    error_handling: Enforce the approved taxonomy and priority values. Apply severity keywords independently. Provide a grounded reason. Flag ambiguity.

  - name: batch_classify
    description: Read the input CSV, process every complaint, and write the required output CSV.
    input: input CSV file path, output CSV file path
    output: None (writes to CSV)
    error_handling: Validate required columns. Handle malformed/missing records safely. Do not silently discard records.
