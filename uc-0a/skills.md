# skills.md

skills:
  - name: classify_complaint
    description: Classifies one civic complaint into the UC-0A schema.
    input: A dictionary-like row with at least a description field and optionally a complaint_id.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: Returns Other, Low, and NEEDS_REVIEW when the description is empty or ambiguous.

  - name: batch_classify
    description: Reads a CSV of complaints and writes a classified results CSV.
    input: A path to an input CSV file and a path to an output CSV file.
    output: A CSV file containing one classified row per input row.
    error_handling: Continues processing even if one row fails and writes a fallback result for that row.
