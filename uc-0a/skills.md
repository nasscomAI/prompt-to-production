# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into exactly one schema category and priority tier, citing verbatim evidence from the description.
    input: dict — one CSV row keyed by column name; only the `description` value drives decisions (`complaint_id` is carried through unchanged).
    output: dict with keys complaint_id (str), category (one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent | Standard | Low), reason (one sentence quoting description text), flag ("NEEDS_REVIEW" or "").
    error_handling: On a missing/empty description or zero category matches, returns category Other with flag NEEDS_REVIEW; on multiple category matches, returns the category whose keyword appears earliest in the text with flag NEEDS_REVIEW; never raises to the caller.

  - name: batch_classify
    description: Reads a city test CSV, applies classify_complaint to every row, and writes one results CSV preserving full row count.
    input: str input_path pointing to ../data/city-test-files/test_[city].csv (header row required) and str output_path for results_[city].csv.
    output: None (side effect only) — writes CSV with header `complaint_id,category,priority,reason,flag`, one row per input row.
    error_handling: Missing/unreadable input file exits non-zero with a clear message before writing anything; malformed rows (nulls, missing columns) are classified as Other/NEEDS_REVIEW rather than skipped; an unexpected error on any single row emits that row as Other/NEEDS_REVIEW so one bad row never aborts the batch.
