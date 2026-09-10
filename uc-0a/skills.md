# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify one complaint row into a closed taxonomy category plus priority, grounded reason, and ambiguity flag.
    input: A dict with at least `complaint_id` (string) and `description` (string, may be null/empty); optionally `location` (string, tie-breaker only).
    output: A dict with exactly `complaint_id` (string), `category` (exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), `priority` (exactly one of Urgent, Standard, Low), `reason` (one English sentence quoting 1–3 words verbatim from the description), `flag` (NEEDS_REVIEW or empty string).
    error_handling: Never raises. If description is null/empty/whitespace or has no category signal, return category Other, priority Low, reason stating the description is missing/vague (quoting location if description is empty), flag NEEDS_REVIEW. If two categories tie on keyword evidence, return the precedence winner per agents.md E5 but set flag NEEDS_REVIEW and note both signals in reason. Severity matching is case-insensitive and covers inflections (injury/injured, child/children, fell/fallen, collapse/collapsed, hospital/hospitalised, hazard/hazardous).

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to every row, and write a results CSV without crashing on bad rows.
    input: `input_path` (path to CSV with at least `complaint_id` and `description` columns) and `output_path` (path to write; parent dirs created if needed).
    output: A CSV file with header `complaint_id,category,priority,reason,flag` and one row per input row, in input order; returns the count of rows written. Prints `Done. Results written to <output_path>`.
    error_handling: Never crashes the batch. Per-row try/except: rows missing complaint_id get a synthetic id `ROW-<line>`; rows that raise (null bytes, bad encoding, missing description) are emitted as category Other, priority Low, reason describing the fault, flag NEEDS_REVIEW. Missing input file raises FileNotFoundError with a clear message; an empty input still writes a header-only output file.
