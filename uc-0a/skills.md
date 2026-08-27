# skills.md

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into category, priority, reason,
      and flag.
    input: One complaint row — a dictionary or CSV row whose fields include the
      complaint description text and any other relevant columns.
    output: A dict with exactly the keys `category`, `priority`, `reason`,
      `flag`, where category is one of Pothole, Flooding, Streetlight, Waste,
      Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other;
      priority is Urgent, Standard, or Low; reason is one sentence citing
      specific words from the description; and flag is NEEDS_REVIEW or blank.
    error_handling: If the description does not support a confident category,
      set category to Other and flag to NEEDS_REVIEW. If the description is
      missing or empty, flag it NEEDS_REVIEW rather than guessing.

  - name: batch_classify
    description: >
      Reads an input complaint CSV, applies classify_complaint to every row, and
      writes the classified results to an output CSV.
    input: A CSV file path (e.g. test_pune.csv) whose rows contain complaint
      descriptions with the `category` and `priority_flag` columns stripped.
    output: A CSV file at the requested path (e.g. results_pune.csv) with one
      row per input row, each containing `category`, `priority`, `reason`, and
      `flag` satisfying the enforcement rules.
    error_handling: Preserve the original row count — never drop or invent rows.
      If a row fails classification or is ambiguous, mark it NEEDS_REVIEW and
      still write it to the output.
