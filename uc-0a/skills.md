# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies one citizen complaint row into an allowed category and priority,
      and returns a citing justification plus a review flag.
    input: >
      dict — one CSV row. Reads only `description` (str) and `complaint_id` (str).
      All other columns (ward, city, location, days_open, reported_by, date_raised)
      are present but deliberately ignored, per the excluded-context rule in agents.md.
    output: >
      dict with exactly five keys in this order — complaint_id (str),
      category (str, one of the 10 allowed), priority (str, Urgent|Standard|Low),
      reason (str, one sentence quoting matched terms from the description),
      flag (str, "NEEDS_REVIEW" or ""). No extra keys are ever added.
    error_handling: >
      Missing or empty description → category Other, priority Standard,
      flag NEEDS_REVIEW, reason "Description is missing or empty; cannot classify."
      Missing complaint_id → caller supplies positional id ROW_<n>.
      No category term matched → Other + NEEDS_REVIEW, never a guessed label.
      Weak evidence (top score < 2.0) or near-tie (top two within 1.5) → best category
      is still returned so the row stays actionable, but flag is NEEDS_REVIEW.

  - name: score_categories
    description: >
      Scores the description against the weighted keyword patterns of all 10 allowed
      categories and returns the ranked evidence, so category choice is auditable
      rather than opaque.
    input: "str — the complaint description, lowercased internally before matching."
    output: >
      list of (category, score, matched_terms) tuples sorted by score descending,
      then by the fixed schema order for deterministic tie-breaking. matched_terms
      holds the literal substrings found in the description, which is what the
      reason field later quotes.
    error_handling: >
      Empty or non-string input → returns an empty list, which the caller treats as
      "no evidence" and resolves to Other + NEEDS_REVIEW. Ties never raise: the schema
      order breaks them deterministically and the near-tie triggers NEEDS_REVIEW.

  - name: detect_severity
    description: >
      Finds severity keywords in the description and is the single authority for
      escalating a complaint to Urgent.
    input: "str — the complaint description."
    output: >
      list of str — the literal matched severity terms as they appear in the text
      (e.g. ["School", "children"]). Empty list means no escalation.
    error_handling: >
      Matches on whole-word boundaries with explicit inflection patterns, so
      'fell' does not match 'fellow' and 'child' does match 'children'.
      Empty or non-string input → empty list, i.e. no false escalation.

  - name: batch_classify
    description: >
      Reads the city test CSV, applies classify_complaint to every row in order, and
      writes results_[city].csv with the five required columns.
    input: >
      input_path (str) — path to ../data/city-test-files/test_[city].csv;
      output_path (str) — path to write results_[city].csv.
    output: >
      Writes the CSV to output_path and returns the number of rows written.
      Prints a null report and a summary (counts by priority, count of NEEDS_REVIEW)
      to stderr so the operator sees data quality before trusting the file.
    error_handling: >
      Missing input file or missing `description` column → clear error to stderr and
      exit code 1, rather than writing an empty file that looks successful.
      A row that raises during classification is caught, written as
      Other / Standard / NEEDS_REVIEW with the exception named in its reason, and the
      batch continues — one bad row never costs the other fourteen.
      Every row is enum-validated immediately before write; an out-of-schema value is
      rewritten as Other + NEEDS_REVIEW rather than being emitted.
      Row count out always equals row count in.