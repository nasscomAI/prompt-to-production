# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag using Claude with RICE enforcement rules.
    input: A dict with at minimum complaint_id (string) and description (string).
    output: A dict with keys complaint_id, category, priority, reason, flag — all strings; flag is empty string when no ambiguity.
    error_handling: If the API call fails or returns an unparseable response, return a result with category "Other", priority "Standard", reason "Classification failed due to API error", flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, classifies all rows in a single Claude API call, and writes the results to an output CSV.
    input: input_path (string path to CSV with columns complaint_id and description), output_path (string path for results CSV).
    output: Writes a CSV at output_path with columns complaint_id, category, priority, reason, flag; one row per input complaint.
    error_handling: If a row is missing the description field, write it to output with category "Other", priority "Standard", reason "Description field missing", flag "NEEDS_REVIEW". Do not crash on individual row failures — continue and flag them.
