skills:
  - name: classify_complaint
    description: Classifies a single complaint row into exact category, priority, reason, and ambiguity flag.
    input: Dict with description field (string) containing complaint text.
    output: Dict with category (string), priority (string), reason (string), flag (string or empty).
    error_handling: Rejects hallucinated or non-schema categories; raises error if priority is Standard or Low but severity keywords present; requires reason to cite specific complaint words; sets flag to NEEDS_REVIEW when category is genuinely ambiguous; refuses confident classification on ambiguous cases.

  - name: batch_classify
    description: Reads input CSV of complaints, applies classify_complaint to each row, writes output CSV with classifications.
    input: File path to input CSV with complaint descriptions; CSV must contain rows with description column.
    output: File path to output CSV with category, priority, reason, flag columns.
    error_handling: Validates all output categories are from allowed list only; detects and rejects category name variations across rows; requires all reason fields to cite complaint words from descriptions; raises error if any row lacks reason field; rejects output if hallucinated categories or high-confidence classifications on ambiguous complaints are detected.