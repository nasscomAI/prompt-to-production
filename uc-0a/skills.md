# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into an exact category enum value, a priority level, and a one-sentence evidence-backed reason.
    input: One CSV row as a dict; requires a non-empty `description`; `complaint_id` expected but optional.
    output: Dict with keys `complaint_id`, `category` (exact enum string), `priority` (Urgent/Standard/Low), `reason` (one sentence quoting words from the description), `flag` (NEEDS_REVIEW or blank).
    error_handling: Empty or missing description returns category Other + flag NEEDS_REVIEW rather than guessing; ambiguous multi-category matches keep the strongest category but set flag NEEDS_REVIEW; unexpected exceptions are converted by the caller into a flagged row, never raised past batch_classify.

  - name: batch_classify
    description: Reads the input complaints CSV, applies classify_complaint to every row, writes the results CSV, and reports a summary with null counts.
    input: Path to test_[city].csv (UTF-8 with header row including complaint_id and description columns) and the output path for results_[city].csv.
    output: Results CSV with header complaint_id, category, priority, reason, flag — exactly one row per input row; returns a summary dict (row count, null report, category/priority tallies) printed to stdout.
    error_handling: Malformed or failing rows never crash the run — they are written as category Other + flag NEEDS_REVIEW with the failure noted in reason; rows lacking complaint_id get ROW-[line-number] placeholders; missing descriptions are counted in the printed null report.
