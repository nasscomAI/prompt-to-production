# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Accepts a single complaint row (dict) and returns a classified output dict
      with category, priority, reason, and flag fields — all validated against
      the UC-0A schema before returning.
    input: >
      dict with at least the key `description` (str). Optional keys:
      `complaint_id` (str), `date_raised`, `city`, `ward`, `location`,
      `reported_by`, `days_open`. All values may be str or empty string.
    output: >
      dict with exactly five keys:
        complaint_id (str)  — copied from input or "UNKNOWN" if absent
        category     (str)  — one of the 10 allowed taxonomy values
        priority     (str)  — one of: Urgent | Standard | Low
        reason       (str)  — one sentence citing description text
        flag         (str)  — "NEEDS_REVIEW" or "" (empty string)
    validation_rules:
      - Category value must be a member of the ALLOWED_CATEGORIES set.
      - Priority value must be a member of {Urgent, Standard, Low}.
      - Reason must be a non-empty string.
      - Flag must be either "NEEDS_REVIEW" or "".
      - If any severity keyword is found in description (case-insensitive),
        priority must be Urgent regardless of other signals.
      - If output fails schema validation, the row is returned with
        category=Other, priority=Low, flag=NEEDS_REVIEW, and the reason
        explains what validation failed — the function never raises an
        exception to the caller.
    assumptions:
      - The `description` field is in English or transliterated English.
      - Descriptions may contain typos; keyword matching uses lower-case
        containment checks, not exact word boundaries.
      - Multiple categories mentioned in one description (e.g., flooding AND
        pothole) are resolved by picking the dominant/first signal and setting
        flag=NEEDS_REVIEW.
    constraints:
      - No external API calls, no ML model inference, no network I/O.
      - Must run in O(n) time relative to description length.
      - Must not mutate the input dict.
    failure_modes:
      - Empty description → category=Other, priority=Low, flag=NEEDS_REVIEW,
        reason="Description was empty or unreadable."
      - Description is non-string type → coerced to str first; if coercion
        fails, treated as empty description.
      - Severity keyword match produces wrong priority → prevented by running
        keyword check AFTER category assignment and overriding priority.
      - Category not in taxonomy → caught by post-classification validation
        and replaced with Other + NEEDS_REVIEW flag.
    testing_strategy:
      - Unit test: each of the 10 categories should be triggered by a
        representative description.
      - Unit test: each of the 9 severity keywords must trigger Urgent.
      - Edge test: empty string, whitespace-only, single-word descriptions.
      - Adversarial test: description mixing two category signals.
      - Adversarial test: severity keyword in a negated context
        ("no injury reported") — current rule still triggers Urgent because
        keyword presence is the rule; human review via NEEDS_REVIEW flag.
    guardrails:
      - Post-classification assert: category in ALLOWED_CATEGORIES.
      - Post-classification assert: priority in {Urgent, Standard, Low}.
      - Post-classification assert: reason is non-empty string.
      - Post-classification assert: flag in {"NEEDS_REVIEW", ""}.
      - Any assert failure falls back to safe defaults instead of crashing.

  - name: batch_classify
    description: >
      Reads the input CSV, applies classify_complaint to every row, collects
      results, and writes a clean output CSV. Partial failures on individual
      rows do not abort the batch; failed rows are written with error metadata
      and NEEDS_REVIEW flag.
    input: >
      input_path  (str) — path to a UTF-8 CSV file with at minimum the columns:
                          complaint_id, description.
      output_path (str) — writable file path for the results CSV.
    output: >
      A CSV file at output_path with columns:
        complaint_id, category, priority, reason, flag
      One row per input row. Function also returns (int, int): (total_rows, error_rows).
    validation_rules:
      - Input file must exist and be readable; if not, raise FileNotFoundError
        with an informative message.
      - Input file must contain at least a `description` column; if not, raise
        ValueError naming the missing column.
      - Output directory must be writable; if not, raise PermissionError.
      - Every row in the output must pass the same schema validation as
        classify_complaint output.
    assumptions:
      - CSV encoding is UTF-8 (falls back to latin-1 on decode error).
      - File may have Windows or Unix line endings; Python's csv.DictReader
        handles both.
      - Input may contain blank rows (skipped with a warning log).
    constraints:
      - Memory: processes rows one at a time (no full in-memory load).
      - Must not overwrite an existing output file without warning (logs a
        warning; still overwrites to support re-runs).
      - Logging at INFO level for each processed row; WARNING for skipped/
        failed rows; ERROR if the whole batch cannot start.
    failure_modes:
      - Missing input file → FileNotFoundError raised immediately with path.
      - Missing `description` column → ValueError raised with column name.
      - Individual row classification error → row written with category=Other,
        priority=Low, flag=NEEDS_REVIEW, reason contains exception message.
      - Output write failure mid-batch → partial file left; error logged and
        re-raised so caller can clean up.
      - Zero rows processed → warning logged; empty output CSV (headers only)
        still written.
    testing_strategy:
      - Integration test: run full pipeline on test_hyderabad.csv, verify
        output has 15 rows with no null fields.
      - Error test: run on a CSV missing the description column.
      - Error test: run on a non-existent file path.
      - Edge test: CSV with one blank row mixed in.
      - Regression test: re-run on same input → identical output (determinism).
    guardrails:
      - Row count in output must equal non-blank row count in input.
      - No cell in the output CSV may contain the strings "None", "nan",
        "NaN", or "null" — checked before writing each row.
      - All output category values must be from the allowed taxonomy.
