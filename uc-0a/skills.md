# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag using the fixed schema.
    input: >
      dict — one complaint row with at least a `description` field (string),
      plus optional context fields (location, ward).
    output: >
      dict — {category: str from the 10 allowed values,
              priority: "Urgent" | "Standard" | "Low",
              reason: str, one sentence citing words from the description,
              flag: "NEEDS_REVIEW" or ""}
    error_handling: >
      Empty or missing description → category "Other", priority "Standard",
      reason stating description was missing, flag "NEEDS_REVIEW".
      Description matching multiple categories → category "Other",
      flag "NEEDS_REVIEW". Any severity keyword found → priority forced
      to "Urgent" before returning.

  - name: batch_classify
    description: Reads a complaints CSV, runs classify_complaint on every row, and writes the classified results to an output CSV.
    input: >
      input_path (str, path to test_[city].csv with header row) and
      output_path (str, path for results_[city].csv).
    output: >
      None — writes results CSV preserving all original columns plus
      category, priority, reason, flag; returns row count written.
    error_handling: >
      Input file not found or empty → exit non-zero with a clear message,
      write nothing. Row with unparseable fields → still emitted via
      classify_complaint's fallback rather than dropped. Output directory
      unwritable → exit non-zero before processing rows.
