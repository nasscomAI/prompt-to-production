skills:
  - name: "classify_complaint"
    description: "Analyzes a single row of complaint text to determine category, priority, and justification."
    input: "Dictionary representing a single CSV row (complaint_id, description)."
    output: "Dictionary with keys: category, priority, reason, flag."
    error_handling: "If severity keywords are detected, priority MUST escalate to Urgent regardless of other context."

  - name: "batch_classify"
    description: "Orchestrates the reading of an input CSV and writing of the classified results CSV."
    input: "File path to input CSV (test_[city].csv)."
    output: "File path to results_[city].csv."
    error_handling: "Must handle null descriptions by flagging them as NEEDS_REVIEW."