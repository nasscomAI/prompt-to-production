skills:
  - name: classify_complaint
    description: >
      Assigns one routing category, one response priority, a source-quoting
      reason and an ambiguity flag to a single citizen complaint record, using
      the complaint description as the only evidence.
    input: >
      One dict representing a CSV row, with at least the keys complaint_id and
      description. Other columns present in the file (date_raised, city, ward,
      location, reported_by, days_open) are accepted but deliberately ignored --
      see the context section of agents.md for why days_open in particular must
      not influence the result.
    output: >
      One dict with exactly five keys. complaint_id echoes the input.
      category is one of the ten permitted strings. priority is Urgent or
      Standard (Low is permitted by the schema but never emitted -- see
      enforcement). reason is one sentence quoting the words from this row's
      description that drove both decisions. flag is NEEDS_REVIEW or an empty
      string.
    error_handling: >
      A missing or empty description yields category Other, priority Standard,
      flag NEEDS_REVIEW and a reason stating that no cue was found -- it never
      raises and never guesses. A description matching no category cue is
      treated the same way. A description matching cues from two or more
      categories returns the first category in rule order with flag
      NEEDS_REVIEW and names the competing categories in the reason, rather
      than silently picking one. A missing complaint_id yields an empty string
      in that field so the row is still emitted and still countable.

  - name: batch_classify
    description: >
      Reads an input complaints CSV, applies classify_complaint to every row in
      file order, and writes a results CSV with one output row per input row.
    input: >
      input_path -- path to data/city-test-files/test_[city].csv.
      output_path -- path to write results_[city].csv.
    output: >
      Writes a CSV with the header complaint_id,category,priority,reason,flag
      and exactly as many data rows as the input had. Returns None; the file is
      the product. Row order matches the input so results can be diffed against
      the source line by line.
    error_handling: >
      Row count is the contract: every input row produces an output row, so a
      row that cannot be classified is emitted as Other / NEEDS_REVIEW rather
      than dropped. A dropped row is worse than a flagged one -- a complaint
      that vanishes is never reviewed, while a flagged one reaches a human.
      An unreadable or missing input file raises rather than writing a partial
      results file, because a truncated results CSV looks like a complete one.
