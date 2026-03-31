# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into a structured output of
      category, priority, reason, and flag.
    input: >
      A dictionary (or CSV row) with at minimum: complaint_id (string) and
      description (string containing the citizen complaint text).
    output: >
      A dictionary with exactly these keys:
        - complaint_id: echoed from input
        - category: one of Pothole, Flooding, Streetlight, Waste, Noise,
          Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        - priority: one of Urgent, Standard, Low
        - reason: one sentence citing specific words from the description
        - flag: NEEDS_REVIEW or blank
    error_handling: >
      If the description is empty, null, or unintelligible, return
      category: Other, priority: Low,
      reason: "Description is missing or unintelligible",
      flag: NEEDS_REVIEW. Never raise an exception — always return a
      complete output dict so the batch pipeline does not break.

  - name: batch_classify
    description: >
      Read an input CSV file, apply classify_complaint to every row, and
      write the results to an output CSV file.
    input: >
      Two file paths: input_path (path to a CSV with complaint_id and
      description columns) and output_path (path where the results CSV
      will be written).
    output: >
      A CSV file at output_path with columns: complaint_id, category,
      priority, reason, flag — one row per input complaint, in the same
      order as the input file.
    error_handling: >
      If a row fails to parse or classify_complaint returns an error for
      that row, log the complaint_id and error, write the row with
      category: Other, priority: Low, reason: "Row processing failed",
      flag: NEEDS_REVIEW, and continue processing remaining rows. The
      batch must never crash partway — it must always produce an output
      file even if some rows are problematic.
