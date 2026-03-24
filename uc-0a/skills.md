# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Parses a single row of citizen complaint text to determine its exact civic category and actionable priority based on rigorous rule-based schema mapping.
    input: Dictionary containing a `description` field with the raw citizen report.
    output: Dictionary appending `category`, `priority`, `reason`, and `flag` mapped perfectly against the taxonomy.
    error_handling: Handles ambiguous complaints by enforcing a NEEDS_REVIEW flag; defaults to generic 'Other' category if completely unrecognizable.

  - name: batch_classify
    description: Streams an input CSV of raw complaints, running `classify_complaint` line-by-line while safeguarding against corrupt dataset rows.
    input: String path to the input CSV and String path for the output CSV target.
    output: Generates a structured CSV file populated with classification labels.
    error_handling: Automatically bypasses blank or malformed CSV rows without causing execution panics, ensuring partial pipeline success.
