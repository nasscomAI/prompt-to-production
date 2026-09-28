# skills.md

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into exactly one taxonomy category, a priority, a one-sentence evidence-quoting reason, and a review flag, applying the enforcement rules in agents.md.
    input: >
      A single complaint as a dict or CSV row mapping strings to strings, with
      these keys: complaint_id (str, e.g. 'PM-202401'), date_raised (str, ISO
      YYYY-MM-DD), city (str), ward (str), location (str), description (str,
      free-text complaint, the only load-bearing field for category and
      priority), reported_by (str), days_open (str or int). One row in, one
      result out; the skill never looks at any other row.
    output: >
      A dict with exactly these five keys. complaint_id (str, echoed unchanged
      from the input). category (str, one of the ten strings in agents.md E1).
      priority (str, one of Urgent, Standard, Low, per agents.md E7 and E8).
      reason (str, exactly one sentence, max 40 words, ending in a full stop,
      containing at least one word of 4+ characters copied verbatim from the
      input description, per agents.md E10). flag (str, either NEEDS_REVIEW or
      the empty string, per agents.md E12). No other keys, no prose, no
      markdown.
    error_handling: >
      Never raises. A missing, empty or whitespace-only description yields
      category Other, priority Standard, reason 'Description field is empty or
      unreadable.' and flag NEEDS_REVIEW. A non-string description is coerced
      with str() and then treated as above. A missing complaint_id is emitted as
      an empty string rather than dropped. An unmatched or genuinely ambiguous
      complaint is not an error: it returns category Other with flag
      NEEDS_REVIEW rather than a confident guess (agents.md E11). A serious
      hazard absent from the E7 keyword list is reported at the priority E7 and
      E8 give it, with the signal named in the reason and flag NEEDS_REVIEW
      (agents.md E9). If any field cannot be produced inside the closed lists,
      the result falls back to Other / Standard / NEEDS_REVIEW rather than
      emitting an out-of-schema value (agents.md E14).

  - name: batch_classify
    description: Reads a city complaint CSV, applies classify_complaint to every row independently, and writes the results CSV required by the README run command.
    input: >
      Two paths as command-line strings: input_path, a CSV with the header
      complaint_id,date_raised,city,ward,location,description,reported_by,
      days_open as produced under ../data/city-test-files/ (15 rows per city,
      with category and priority_flag already stripped); and output_path, the
      file to write, expected as uc-0a/results_[city].csv. All source values
      are read as strings; the input file is never modified and never
      rewritten.
    output: >
      Writes output_path as UTF-8 CSV with the header
      complaint_id,category,priority,reason,flag and exactly those five
      columns, one row per input row, in the input order, with no blank
      category, priority or reason cells. The output excludes the stripped
      columns and the descriptive fields that are not part of the schema. The
      file is written even when some rows fail to classify. Returns a counts
      dict for verification — rows_read, rows_written and rows_flagged (int) —
      which the caller may print alongside its completion message.
    error_handling: >
      A missing or unreadable input path raises a clear FileNotFoundError
      naming the path, and no output file is created or truncated. A row with
      missing or empty fields is not dropped: it is passed to
      classify_complaint, which applies its empty-description fallback. A row
      that raises inside classify_complaint is caught individually, emitted as
      Other / Standard / NEEDS_REVIEW with a reason naming the error type, and
      the loop continues — one bad row must never abort the run or reduce the
      output row count below the input row count. A malformed row (ragged field
      count or unparseable quoting) is treated as the missing-field case
      rather than an exception. Wholly blank trailing lines in the input are
      skipped; a blank description inside a real row is not. Rows are
      classified independently with no shared state, so no row's result can
      depend on another row's (agents.md E13). Enforced at write time: any
      value outside the closed category, priority and flag sets is coerced to
      Other / Standard / NEEDS_REVIEW before the row is written (agents.md
      E14).
