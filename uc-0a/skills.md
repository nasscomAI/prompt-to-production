# skills.md

skills:
  - name: classify_complaint
    description: >
      Classifies one complaint row into category, priority, reason, and flag using
      the README taxonomy, severity keywords, and justification rules.
    input: >
      One dict row with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open.
    output: >
      One dict with keys: complaint_id (unchanged), category (exact allowed value),
      priority (Urgent, Standard, or Low), reason (one sentence citing specific words
      from description), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If no category keyword matches the description, returns category: Other and
      flag: NEEDS_REVIEW. Never fabricates facts, categories, or priorities.

  - name: batch_classify
    description: >
      Reads an input CSV of complaint rows, applies classify_complaint to every row,
      and writes a results CSV with the exact output schema.
    input: >
      Path to a test_[city].csv file with header row containing the input columns;
      category and priority_flag columns are stripped and must not be read.
    output: >
      Path to a results CSV with header: complaint_id,category,priority,reason,flag.
      Contains exactly one row per input complaint_id.
    error_handling: >
      Skips rows that cannot be parsed (keeping their complaint_id in the output with
      flag: NEEDS_REVIEW), never crashes the batch, and always writes an output file
      even if some rows fail.