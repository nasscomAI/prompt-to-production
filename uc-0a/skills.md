# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    role: >
      A data processing function responsible for classifying a single citizen complaint row based on text analysis.
    intent: >
      Evaluate a single complaint row's text against predefined keywords to return structured categorization.
    context: >
      This skill parses the "description" field of a complaint row. It matches against category keywords and severity triggers as defined by the main agent rules.
    enforcement:
      - "Must output exactly four fields extracted from the text: category, priority, reason, flag."
      - "If input is ambiguous or unclear, must default to category Other and flag NEEDS_REVIEW."
      - "Must not throw unstructured errors on bad inputs."

  - name: batch_classify
    role: >
      A robust pipeline orchestrator that processes batches of citizen complaints from CSV files.
    intent: >
      Read an input CSV file, systematically apply `classify_complaint` to each row, and write the formatted results to an output CSV file.
    context: >
      Handles file I/O and loops through records. The input files may contain missing data or malformed rows.
    enforcement:
      - "Must handle missing data and skip corrupted rows without crashing the entire batch."
      - "Must log errors encountered during row processing."
      - "Must raise a clear error and exit gracefully if the input file does not exist."
      - "Must successfully write out all successfully classified records to the target output path."
