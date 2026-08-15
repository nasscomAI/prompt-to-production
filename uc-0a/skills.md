# skills.md

skills:
  - name: classify_complaint
    description: >
      Classifies one citizen complaint row into an allowed category plus priority, reason,
      and optional flag, strictly following the UC-0A enforcement rules.
    input: >
      One complaint row as a dict with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open.
    output: >
      A dict with keys: complaint_id, category, priority, reason, flag —
      category one of the 10 allowed strings, priority one of Urgent/Standard/Low,
      reason a single sentence quoting words from the description, flag blank or NEEDS_REVIEW.
    error_handling: >
      If no category is clearly supported by the description, returns category: Other,
      flag: NEEDS_REVIEW, and a reason that states which words made it ambiguous.

  - name: batch_classify
    description: >
      Reads an input CSV, applies classify_complaint to every row, and writes the
      results CSV with the same complaint order.
    input: >
      A path to a test_[city].csv file with the standard header row.
    output: >
      A results_[city].csv file with columns: complaint_id, category, priority, reason, flag.
      One row per input row.
    error_handling: >
      Skips rows that are malformed or fail to parse and writes a warning for each;
      never crashes the whole run. Blank category/priority values in a row are treated as
      missing data and routed to Other + NEEDS_REVIEW instead of being silently dropped.
