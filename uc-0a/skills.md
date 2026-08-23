# skills.md

skills:
  - name: classify_complaint
    description: >
      Given a single complaint description string, return a structured classification
      with category, priority, reason, and optional flag.
    input: >
      A single string (the complaint description), e.g. "Large pothole on
      MG Road near the school entrance."
    output: >
      A JSON object with keys: category (string), priority (string), reason
      (string), flag (string or null).
    error_handling: >
      If the description is empty or unintelligible, set category: "Other",
      priority: "Standard", reason: "Description was empty or unintelligible",
      flag: "NEEDS_REVIEW".

  - name: batch_classify
    description: >
      Read an input CSV with a description column, apply classify_complaint to
      each row, and write the output CSV with category, priority, reason, flag.
    input: >
      Path to an input CSV file (must contain a `description` column) and an
      output CSV file path.
    output: >
      A CSV file at the specified output path, with columns: category,
      priority, reason, flag.  The column order matches the schema.
    error_handling: >
      If the input CSV is missing the `description` column, raise a
      ValueError.  If any row fails classification, write "Other" /
      "Standard" / "Classification error" / "NEEDS_REVIEW" for that row and
      continue.
