# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a category, assigns a priority level, provides a reason, and sets an escalation flag.
    input: A dict representing one CSV row — must include a complaint description field (str); may include complaint_id and other metadata.
    output: A dict with keys — complaint_id (str), category (str), priority (str), reason (str), flag (bool).
    error_handling: If the description is null, empty, or unparseable, set flag=true and return a default/unknown category with low priority; do not raise an exception.
    urgency_keywords: If any of the following words appear in the complaint description (case-insensitive), override priority to "Urgent" and set flag=true regardless of other signals — injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes a results CSV with classification columns appended.
    input: input_path (str) — path to a CSV file with a header row and one complaint per row; output_path (str) — path to write the results CSV.
    output: A CSV file at output_path containing all original columns plus category, priority, reason, and flag for each row.
    error_handling: Skip and log rows that cause errors (do not crash); flag null or malformed rows; always produce an output file even if some rows fail.
