# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dict with a complaint_id and a complaint description text.
    output: A dict with keys: complaint_id, category, priority, reason, flag.
    error_handling: When the description contains no supported category signal, returns category: Other with flag: NEEDS_REVIEW; when severity keywords are present, sets priority: Urgent.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Path to a test CSV with one complaint per row and category/priority columns stripped.
    output: A results CSV with complaint_id, category, priority, reason, flag for every input row in the same order.
    error_handling: Flags nulls, never crashes on bad rows, and produces output even if some rows fail.
