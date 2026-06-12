skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into category, priority, reason,
      and flag using only the complaint description text.
    input: >
      One complaint record as a dictionary or CSV row containing at minimum a
      description field (string). Ground-truth category and priority_flag columns
      are not available and must not be used.
    output: >
      Dictionary with four fields: category (exact allowed schema value),
      priority (Urgent, Standard, or Low), reason (one sentence citing specific
      words from the description), and flag (NEEDS_REVIEW or blank string).
    error_handling: >
      If description is missing or empty, return category Other, priority Low,
      reason stating the description is missing, and flag NEEDS_REVIEW. If category
      is genuinely ambiguous, return category Other and flag NEEDS_REVIEW rather
      than guessing. If severity keywords (injury, child, school, hospital,
      ambulance, fire, hazard, fell, collapse) appear, set priority to Urgent.
      Reject or remap any category not in the allowed list to Other with
      NEEDS_REVIEW. Never omit the reason field. Never invent sub-categories or
      alternate label variants.

  - name: batch_classify
    description: >
      Reads an input CSV of complaint rows, applies classify_complaint to each row,
      and writes a results CSV with classification fields appended.
    input: >
      File path to input CSV (e.g. ../data/city-test-files/test_[city].csv)
      containing complaint rows with a description column; category and
      priority_flag columns are absent.
    output: >
      File path to output CSV (e.g. results_[city].csv) with all input columns
      preserved plus category, priority, reason, and flag columns for every row.
    error_handling: >
      If the input file is missing or unreadable, raise a clear file error and
      do not write partial output. If a row fails classification, still emit an
      output row with category Other, flag NEEDS_REVIEW, and a reason explaining
      the failure — never skip rows silently. Validate every output row has all
      four classification fields before writing. Ensure consistent category labels
      across rows describing the same complaint type to prevent taxonomy drift.
