# skills.md

skills:
  - name: classify_complaint
    description: Classify one citizen complaint row into an allowed category, a justified priority, a cited reason, and an optional review flag.
    input: A single complaint record containing free-text description of the issue.
    output: A dict with keys category, priority, reason, flag — category is exactly one allowed string, priority is Urgent/Standard/Low, reason is one sentence quoting words from the description, flag is NEEDS_REVIEW when ambiguous else empty.
    error_handling: If the description is empty, missing, or cannot be mapped to an allowed category, return category: Other, priority: Standard, flag: NEEDS_REVIEW rather than guessing.

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to every row, and write the results to an output CSV.
    input: Path to input CSV (one complaint per row) and path to output CSV.
    output: A CSV file with one result row per input row, each carrying category, priority, reason, and flag.
    error_handling: Preserve the row count from input to output; if any single row fails, mark it NEEDS_REVIEW and continue so no complaint is silently dropped.
