# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Accepts a single complaint row dict and returns a classification dict with
      category, priority, reason, and flag, enforcing the allowed taxonomy and
      severity-keyword rules without any LLM call.
    input: >
      dict with at least a 'description' string field and a 'complaint_id' string field.
    output: >
      dict with keys: complaint_id (str), category (one of 10 allowed strings),
      priority ('Urgent' | 'Standard' | 'Low'), reason (str, one sentence quoting
      description words), flag ('NEEDS_REVIEW' | '').
    error_handling: >
      If description is missing or empty, set category='Other', priority='Low',
      reason='No description provided', flag='NEEDS_REVIEW'.
      If classification is ambiguous between two valid categories, pick the most
      prominent signal and set flag='NEEDS_REVIEW'.
      Never raise an exception for bad input — always return a valid output dict.

  - name: batch_classify
    description: >
      Reads an input CSV file row-by-row, calls classify_complaint on each row,
      and writes all results to an output CSV file with a fixed column order.
    input: >
      input_path (str): path to a CSV file with at minimum columns complaint_id
      and description.
      output_path (str): path where the results CSV will be written.
    output: >
      A CSV file at output_path with columns:
      complaint_id, category, priority, reason, flag.
      One row per input row, preserving row order.
    error_handling: >
      If an individual row fails classification, write a row with category='Other',
      priority='Low', reason='Classification error', flag='NEEDS_REVIEW' rather
      than crashing the whole batch. Log the error to stderr. If the input file
      cannot be opened, raise FileNotFoundError with a clear message.
