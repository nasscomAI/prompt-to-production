skills:
  - name: classify_complaint
    description: >
      Accepts a single complaint row and returns a structured classification record
      with exactly four fields — category, priority, reason, and flag — following
      the enforcement rules in agents.md.
    input: >
      A dict (or CSV row) with keys: complaint_id, date_raised, city, ward,
      location, description, reported_by, days_open. The 'description' field is
      the primary evidence source; all other fields are supporting context.
    output: >
      A dict with four keys:
        complaint_id  — echoed from input (string)
        category      — one of: Pothole | Flooding | Streetlight | Waste | Noise |
                        Road Damage | Heritage Damage | Heat Hazard | Drain Blockage | Other
        priority      — one of: Urgent | Standard | Low
        reason        — single sentence quoting a specific phrase from description
        flag          — "NEEDS_REVIEW" | "" (empty string)
    error_handling: >
      If 'description' is empty or missing, output category: "Other",
      priority: "Low", reason: "No description provided — cannot classify.",
      flag: "NEEDS_REVIEW". If a keyword match is ambiguous (e.g., description
      mentions 'school' as a nearby landmark rather than a safety risk), apply
      Urgent and note the uncertainty in the reason field rather than suppressing it.
      Never silently drop rows.

  - name: batch_classify
    description: >
      Reads a CSV file of citizen complaints, applies classify_complaint to every
      row, and writes the output to a results CSV — preserving the original columns
      and appending category, priority, reason, and flag.
    input: >
      --input  : path to a CSV file matching the schema:
                 complaint_id, date_raised, city, ward, location, description,
                 reported_by, days_open
      --output : path where the results CSV should be written
      The CSV must be UTF-8 encoded. Whitespace-only description cells are treated
      as empty (triggers the classify_complaint error path).
    output: >
      A CSV file at the --output path containing all original columns plus four
      appended columns: category, priority, reason, flag. Row order is preserved.
      One results row per input row — no rows are skipped or merged.
    error_handling: >
      If the --input file does not exist or is not readable, exit with a non-zero
      code and print: "ERROR: Input file not found: <path>". If a required column
      is missing from the CSV header, exit with: "ERROR: Missing column: <name>".
      Rows with parse errors are written with category: "Other", flag: "NEEDS_REVIEW",
      and a reason explaining the parse failure — processing continues for remaining rows.
