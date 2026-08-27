# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag.
    input: A single dict with at least the keys complaint_id and description, optionally location, ward, city, date_raised, reported_by, days_open.
    output: A dict with exactly the keys complaint_id, category, priority, reason, flag. category is one of the 10 allowed strings; priority is Urgent/Standard/Low; reason is one sentence quoting words from the description; flag is "NEEDS_REVIEW" or "".
    error_handling: Missing or empty description → category "Other", flag "NEEDS_REVIEW", reason stating the description was empty. Description not confidently matching a named category → category "Other" and flag "NEEDS_REVIEW" (never a guessed category). Missing complaint_id → preserve row order but leave complaint_id blank rather than failing.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: A path to a test_[city].csv file with a header row.
    output: Writes a CSV with header complaint_id,category,priority,reason,flag to the given output path, with exactly one row per input row.
    error_handling: Skips nothing and never crashes on a bad row — a malformed or unreadable row still produces an output row with flag "NEEDS_REVIEW". Uses utf-8 encoding. Overwrites the output file if it exists. Reports how many rows were classified and how many were flagged after writing.
