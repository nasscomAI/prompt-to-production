# skills.md

skills:
    - name: classify_single_complaint
    description: Classifies a single complaint text into fixed category taxonomy.
    input: dict with complaint_id (str) and description/text (str, may be null/empty)
    output: dict with complaint_id, category (enum), priority_flag (Urgent/Routine/Low), reason (string quoting source words), confidence (High/Medium/Low)
    error_handling: If null/empty, returns category=Other, priority=Low, confidence=Low, reason='empty/null input flagged'. If ambiguous, returns confidence=Low with reason stating ambiguity. Never crashes.

    - name: batch_classify_csv
    description: Reads input CSV and writes classified results CSV for all rows.
    input: input_path (str CSV), output_path (str CSV)
    output: CSV file with columns complaint_id, category, priority_flag, reason, confidence. Preserves order, flags nulls, skips bad rows with Other/Low.
    error_handling: Handles missing file, bad encoding, missing columns — logs and produces row with Other category for that row, never crashes whole batch.
