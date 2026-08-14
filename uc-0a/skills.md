# skills.md — UC-0A Complaint Classifier
# Generated from the RICE prompt and refined against classifier.py.

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into category, priority, reason and flag.
    input: dict with the complaint row fields, including description (string).
    output: dict with keys complaint_id, category, priority, reason, flag.
    error_handling: A missing or empty description returns category Other, priority Standard and flag NEEDS_REVIEW; content that matches no category maps to Other without a flag.

  - name: batch_classify
    description: Reads an input test_[city].csv, applies classify_complaint to every row and writes results_[city].csv.
    input: input_path (path to test_[city].csv) and output_path (path to the results CSV).
    output: writes a CSV with the original columns plus category, priority, reason and flag; prints row counts and skipped rows.
    error_handling: Missing required columns raise a clear ValueError; a single bad row is skipped with a printed warning while the rest of the file is still produced.