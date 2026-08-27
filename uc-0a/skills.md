# skills.md
skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag using the UC-0A taxonomy and urgency rules.
    input: One complaint record with a non-empty description string.
    output: category, priority, reason, and flag where category is one allowed label; priority is Urgent when severity keywords appear, otherwise Standard; reason is one sentence citing words from the description; flag is NEEDS_REVIEW or blank.
    error_handling: If description is missing or empty, return category Other, priority Standard, a one-sentence reason indicating insufficient text, and flag NEEDS_REVIEW. If the category is truly unclear from description text, return category Other and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a city test CSV, applies classify_complaint to each row, and writes the result CSV with required output fields.
    input: Input CSV path in the test_[city].csv format with complaint description text per row.
    output: Output CSV path in the results_[city].csv format containing category, priority, reason, and flag for every row.
    error_handling: If input file is missing, unreadable, or malformed, stop processing with a clear error. For row-level ambiguity, continue processing and emit category Other with flag NEEDS_REVIEW for that row.
