# skills.md
# Defined Skills for Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into exactly one allowed category and determines its priority (Urgent/Standard/Low).
    input: dict representing a single CSV row, must contain a complaint description field.
    output: dict containing exactly: complaint_id, category, priority, reason, flag.
    error_handling: If classification is genuinely ambiguous, assigns 'Other' (or closest match) and sets flag to 'NEEDS_REVIEW' instead of hallucinating categories.

  - name: batch_classify
    description: Reads a dataset of complaints, applies the classify_complaint skill sequentially without failing the entire batch on a bad row.
    input: str input_path (CSV), str output_path (CSV).
    output: Writes parsed CSV results to the output_path.
    error_handling: Wraps individual row processing in a try/except clause to ensure partial failures do not crash the batch job.
