# skills.md

skills:
  - name: classify_complaint
    description: Receives a single complaint row, extracts the core issue, and classifies it within rigid schematic constraints.
    input: Dictionary containing 'description' and other metadata fields.
    output: Dictionary appending `category`, `priority`, `reason`, and `flag` fields.
    error_handling: In cases of severe lack of detail or unparseable multi-issue complaints, returns category "Other" with flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes a full CSV of complaints sequentially without crashing on unparseable rows.
    input: String path to an input CSV.
    output: String path to the written output CSV.
    error_handling: Bypasses failed rows, logging them, and processes the rest of the batch, guaranteeing an output file is always generated.
