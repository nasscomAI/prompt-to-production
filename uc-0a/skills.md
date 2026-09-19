# UC-0A skills

skills:
  - name: classify_complaint
    description: Classify one complaint row into the fixed taxonomy with severity, evidence, and an ambiguity flag.
    input: A dictionary containing complaint_id and a text description.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: Missing or non-text descriptions become Other/Standard with NEEDS_REVIEW; unsupported categories are never invented.

  - name: batch_classify
    description: Read a complaint CSV, classify each row independently, and write a schema-valid results CSV.
    input: Input CSV path and output CSV path.
    output: CSV with complaint_id, category, priority, reason, and flag for every input row.
    error_handling: Malformed rows are emitted as Other with NEEDS_REVIEW so one bad row does not stop the batch.
