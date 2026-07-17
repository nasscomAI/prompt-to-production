# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason and flag using the locked schema in agents.md.
    input: dict with at least complaint_id and description (strings); other CSV columns are present but must be ignored.
    output: dict with exactly complaint_id, category (one of the 10 allowed values), priority (Urgent | Standard | Low), reason (one sentence citing words from the description), flag (NEEDS_REVIEW or empty string).
    error_handling: Empty or missing description returns category Other, priority Standard, flag NEEDS_REVIEW with reason stating the description was missing. Ambiguous matches (0 keywords, tied categories, or weak-only keywords) keep the best-guess category but always set flag NEEDS_REVIEW — never a confident guess.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, writes the results CSV.
    input: input_path to test_[city].csv and output_path for results_[city].csv (strings).
    output: CSV file with header complaint_id, category, priority, reason, flag — one row per input row, written even if some rows fail.
    error_handling: A row that raises is written as complaint_id (or UNKNOWN), category Other, flag NEEDS_REVIEW with the error in the reason — the batch never crashes and never silently drops a row.
