skills:
  - name: classify_complaint
    description: Classifies a citizen complaint by extracting a strictly allowed category, identifying priority based on severity keywords (injury, child, school, fire, etc.), and generating a one-sentence reason citing the description.
    input: Dictionary representation of a single CSV row, specifically using the 'description' field.
    output: Dictionary containing strictly formatted fields [complaint_id, category, priority, reason, flag] as required by agents.md.
    error_handling: If the description is too ambiguous to map to an exact category, the category defaults to 'Other' and the flag is set to 'NEEDS_REVIEW' as enforced by agents.md rules.

  - name: batch_classify
    description: Coordinates reading multiple rows from the source CSV, isolating each row against classify_complaint, and seamlessly generating the result payload.
    input: Two strings representing the input file path and output file path.
    output: A newly written output CSV file with identical row counts to the input, appending the required classification fields.
    error_handling: Automatically skips formatting errors on bad lines safely without stalling the broader classification batch. Flags row with 'NEEDS_REVIEW'.
