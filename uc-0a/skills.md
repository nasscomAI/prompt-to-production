skills:
  - name: classify_complaint
    description: >
      Assigns one complaint row a category from the permitted set, a priority, a
      one-sentence reason citing that row's description, and an ambiguity flag.
    input: >
      dict — one row of test_[city].csv, carrying at least complaint_id and
      description. Classification is derived from the description alone. The
      ward and location fields hold place names only, and treating a place name
      as category evidence would violate the locative exclusion in enforcement
      rule 4, so they are not read. days_open, reported_by, city and the
      complaint_id prefix are likewise not read.
    output: >
      dict with exactly five keys — complaint_id (str, copied from the input),
      category (str, one of the ten permitted values), priority (Urgent, Standard
      or Low), reason (str, one sentence quoting at least one word present in the
      description), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      A row with a blank description returns category Other, priority Standard,
      flag NEEDS_REVIEW and a reason naming the absent field, since there is
      nothing to classify or to cite. A row with a blank complaint_id is
      classified normally and flagged NEEDS_REVIEW, keeping whatever priority its
      description earns: enforcement rule 2 forbids downgrading a severity match,
      so an injury is not recorded as Standard because an identifier was
      missing. Two or more categories supported equally return Other with
      NEEDS_REVIEW rather than the first match. A category outside the permitted
      set is downgraded to Other with NEEDS_REVIEW rather than emitted. Field
      values are coerced to str before use rather than assumed to be strings,
      because csv.DictReader yields a list for a row carrying more fields than
      the header and a caller may pass any type. The function never raises:
      every input, including a malformed or non-string one, returns a
      well-formed five-key dict.

  - name: batch_classify
    description: >
      Reads the input CSV, applies classify_complaint to every row in source
      order, and writes the results CSV.
    input: >
      input_path (str) — path to test_[city].csv; output_path (str) — path to
      write the results CSV.
    output: >
      CSV at output_path with header complaint_id,category,priority,reason,flag
      and exactly one row per input row, in input order. Returns counts of rows
      written, rows flagged, and rows marked Urgent.
    error_handling: >
      A row whose classification raises is written as an Other/NEEDS_REVIEW row
      naming the failure, never skipped, so the output row count always equals
      the input row count. A missing or unreadable input file fails with the path
      named before any output is written. The file is read as utf-8-sig so a byte
      order mark cannot corrupt the first column name.
