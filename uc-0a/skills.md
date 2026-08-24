skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag per the fixed taxonomy and severity rules.
    input: >
      One complaint row dict with keys complaint_id (string), description (string),
      plus optional ward/location. Description is the sole signal for classification.
    output: >
      Dict with keys complaint_id (string), category (one of 10 allowed exact strings),
      priority (Urgent/Standard/Low), reason (one sentence citing specific words from description),
      flag (NEEDS_REVIEW or blank). Category never hallucinated; priority Urgent iff severity keywords present.
    error_handling: >
      If description missing/blank → category Other, priority Standard, flag NEEDS_REVIEW,
      reason cites "empty description". If 2+ categories tie for top keyword score → pick highest-priority match
      but set flag NEEDS_REVIEW and reason notes ambiguity. Never invent sub-categories; on genuine ambiguity return
      category Other + NEEDS_REVIEW. Severity keywords are case-insensitive: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes results CSV with validation and fault tolerance.
    input: >
      input_path (string path to test_[city].csv) and output_path (string path to results_[city].csv).
      Input CSV expected columns: complaint_id, description, etc. Only description used for classification.
    output: >
      CSV written to output_path with header complaint_id,category,priority,reason,flag (15 rows for city test files).
      Returns count of processed rows and count flagged NEEDS_REVIEW. Creates parent dirs if needed.
    error_handling: >
      Validates file exists and has complaint_id + description columns; if missing, raises ValueError with clear message.
      Skips malformed rows but logs to stderr and continues; blank description handled by classify_complaint as Other+NEEDS_REVIEW.
      Never crashes on bad rows — produces output for all readable rows. Overwrites output_path atomically.
      Reports taxonomy violations (invalid category strings) before writing.
