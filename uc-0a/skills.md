# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority level, reason, and review flag.
    input: >
      A dictionary (dict) representing one CSV row with at least these keys:
      complaint_id (string or int) and description (free-text string).
    output: >
      A dictionary with exactly these keys:
      complaint_id (string) — the original complaint ID;
      category (string) — one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other;
      priority (string) — one of: Urgent, Standard, Low;
      reason (string) — one sentence citing specific words from the description;
      flag (string) — "NEEDS_REVIEW" if category is ambiguous or Other, otherwise blank "".
    error_handling: >
      If description is empty, null, or contains no meaningful text, return
      category: "Other", priority: "Low", reason: "Description is empty or missing",
      flag: "NEEDS_REVIEW". If complaint_id is missing, generate a placeholder ID
      prefixed with "UNKNOWN_" and set flag: "NEEDS_REVIEW". Never raise an
      exception; always return a valid output dictionary.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the classification results to an output CSV file.
    input: >
      Two file path strings: input_path (path to a CSV file with complaint rows)
      and output_path (path where the results CSV will be written).
    output: >
      A CSV file written to output_path with columns: complaint_id, category,
      priority, reason, flag. One row per input complaint. Returns None (writes
      to file as a side effect).
    error_handling: >
      If a row fails to parse or causes an error, log a warning and write a row
      with category: "Other", priority: "Low", reason: "Row failed to process",
      flag: "NEEDS_REVIEW" — do not skip the row or crash. If the input file is
      missing or unreadable, raise a FileNotFoundError with a clear message.
      If the input file has zero data rows, write an output CSV with headers only.
