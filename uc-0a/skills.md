# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag per agents.md.
    input: One row (dict) with at least description; other columns (id, location, date, etc.) pass through unused. description may be missing or empty.
    output: The row's fields plus category (exact enum string), priority (Urgent/Standard/Low), reason (one sentence citing description text), flag (NEEDS_REVIEW or blank). All four always present, never null.
    error_handling: >
      Never raises. Missing/empty description → category=Other,
      priority=Standard, flag=NEEDS_REVIEW, reason="No description was
      provided." Genuine ambiguity (vague description, or 2+ plausible
      categories) → best-guess category (or Other), flag=NEEDS_REVIEW,
      reason names the ambiguity. Never emits a value outside the defined
      enums.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, writes the output CSV.
    input: input_path (CSV with a description column plus original fields; category/priority absent). output_path (where to write results).
    output: A CSV at output_path with every input row, same order, original columns preserved, plus category/priority/reason/flag appended. Row count matches input exactly.
    error_handling: >
      Missing input file or no description column = structural failure:
      fail fast, write nothing. Once processing starts, one bad row
      (e.g. unreadable text) is written with the classify_complaint
      fallback (Other/Standard/NEEDS_REVIEW) and processing continues —
      never aborts the batch, never writes a partial or truncated file.
