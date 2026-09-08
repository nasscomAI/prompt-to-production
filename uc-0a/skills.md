# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row from a citizen issue description into the UC-0A category, priority, justification reason, and review flag.
    input: One complaint row object or mapping containing at least a description field and optionally a complaint_id or other row metadata; input is a CSV row dictionary.
    output: A dictionary with keys complaint_id, category, priority, reason, and flag that follows the UC-0A schema exactly.
    error_handling: If the description is missing or not enough evidence exists to determine a category, emit category Other and flag NEEDS_REVIEW; do not invent a category or confidence that is not supported by the text.

  - name: batch_classify
    description: Read an input CSV file, apply classify_complaint to every complaint row, and write a results CSV file that preserves the UC-0A output schema.
    input: A file path to an input CSV with complaint description rows and an output file path where the classified results CSV should be written.
    output: A CSV file with the rows classified by classify_complaint, including category, priority, reason, and flag fields for each complaint.
    error_handling: If a row is invalid, empty, or ambiguous, preserve the row in the output with category Other, flag NEEDS_REVIEW, and a reason that cites the text or explains that the issue cannot be determined from the description alone instead of crashing or dropping the row.
