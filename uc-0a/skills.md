skills:
  - name: classify_complaint
    description: >
      Classifies one complaint row into an allowed category, priority, reason,
      and optional NEEDS_REVIEW flag using only the row description.
    input: >
      One CSV row dict including at least complaint_id and description
      (other fields optional).
    output: >
      Dict with keys: complaint_id, category, priority, reason, flag
      (flag is NEEDS_REVIEW or blank). Category is an exact taxonomy string;
      reason cites words from the description.
    error_handling: >
      If description is missing/blank or category is ambiguous, return
      category Other, priority based on severity keywords if any else Low,
      reason explaining the gap, and flag NEEDS_REVIEW. Never invent a
      non-taxonomy category. Always include reason.

  - name: batch_classify
    description: >
      Reads the city test CSV, applies classify_complaint to each row, and
      writes the results CSV without aborting on bad rows.
    input: >
      Path to test_[city].csv and path for results_[city].csv.
    output: >
      Results CSV with columns complaint_id, category, priority, reason, flag
      — one row per input row (including failed/null rows flagged).
    error_handling: >
      Skip-crash policy: on malformed rows, write a NEEDS_REVIEW result and
      continue. If the input file is missing or unreadable, raise a clear
      error. Do not drop rows silently.
