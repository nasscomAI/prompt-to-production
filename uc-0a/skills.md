# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into a fixed category, priority, one-sentence quoted reason, and review flag.
    input: A dict with `complaint_id` (string) and `description` (string); description must be non-empty text.
    output: A dict with `complaint_id` (string), `category` (exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), `priority` (Urgent, Standard, or Low), `reason` (one sentence quoting words from the description), and `flag` (NEEDS_REVIEW or empty string).
    error_handling: If description is missing, null, or blank, returns category Other, priority Standard, a reason stating the description was missing, and flag NEEDS_REVIEW; never raises on a single bad row.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes a results CSV.
    input: `input_path` (path to CSV with complaint_id and description columns) and `output_path` (path to write CSV with complaint_id, category, priority, reason, flag columns).
    output: A CSV file at output_path with one row per input row in input order, plus a count summary printed to stdout.
    error_handling: Skips no rows — null or malformed rows become Other/NEEDS_REVIEW entries; per-row exceptions are caught and converted to NEEDS_REVIEW rows so the batch always completes and always writes output.
