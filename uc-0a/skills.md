# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row into category + priority + reason + flag per agents.md enforcement.
    input: Dict with `complaint_id` (string), `description` (string), `location` (string, optional tiebreaker). Example: {"complaint_id": "PM-202402", "description": "Deep pothole near bus stop. School children at risk during morning hours.", "location": "FC Road near MIT College junction"}.
    output: Dict with `complaint_id` (echoed), `category` (exact string from closed taxonomy of 10), `priority` (Urgent/Standard/Low per severity-override rule), `reason` (one sentence quoting 2+ consecutive words from description), `flag` (NEEDS_REVIEW or ""). Example: {"complaint_id": "PM-202402", "category": "Pothole", "priority": "Urgent", "reason": "Localized pothole with 'School children at risk' triggering severity override.", "flag": ""}.
    error_handling: If description is null/empty/vague, return category Other, priority Standard, reason stating the description is missing/vague (quoting location if description absent), flag NEEDS_REVIEW — never throw, never invent a category.

  - name: batch_classify
    description: Read input test CSV, apply classify_complaint to every row, write fixed-schema results CSV.
    input: "input_path (string path to test_[city].csv with columns complaint_id,description,location,...) and output_path (string path to results_[city].csv)."
    output: "CSV at output_path with header complaint_id,category,priority,reason,flag and exactly one row per input row in input order, including rows that failed to classify (mapped to Other/Standard/NEEDS_REVIEW)."
    error_handling: Never crash on bad rows (null description, missing complaint_id, extra columns, bad encoding): flag the row NEEDS_REVIEW, assign category Other, continue processing. Create parent directories if needed. Always produce the output file even if some rows fail; log per-row warnings to stderr.
