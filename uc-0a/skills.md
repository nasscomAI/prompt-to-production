# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Takes a single complaint description string and returns a structured classification with category, priority, reason, and flag.
    input: >
      A single string — the complaint description text from one CSV row.
      No other fields (ward, city, complainant ID) are passed or used.
    output: >
      A dict with four keys:
        category  — exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
                    Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        priority  — exactly one of: Urgent, Standard, Low
        reason    — one sentence quoting specific words from the input description
        flag      — "NEEDS_REVIEW" if category is ambiguous, otherwise empty string
    error_handling: >
      If the description is empty or contains no classifiable content, return
      category: Other, priority: Low, reason: "Description provided no classifiable
      content.", flag: NEEDS_REVIEW. Never raise an exception — always return a
      complete four-field dict.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each description, and writes a results CSV with the original fields plus the four classification columns.
    input: >
      Two file paths as strings:
        input_path  — path to the source CSV (must contain a "description" column)
        output_path — path where the results CSV will be written
    output: >
      A CSV file at output_path containing all original columns plus:
        category, priority, reason, flag
      Row count in output must equal row count in input.
      Also returns a summary dict: { total: int, urgent: int, needs_review: int }
    error_handling: >
      If input_path does not exist or lacks a "description" column, print a clear
      error message and exit without writing output. If an individual row fails
      classification, write category: Other, flag: NEEDS_REVIEW for that row and
      continue — do not abort the batch.
