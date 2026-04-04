# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    role: >
      An atomic classification worker that processes a single citizen complaint row.
    intent: >
      To map a complaint's description to its predefined category, evaluate severity for its priority level, extract a one-sentence reason citing the text, and flag ambiguities.
    context: >
      Operates purely on the text of a single complaint row. It lacks broader system knowledge and evaluates description text strictly without hallucination or generalization.
    enforcement:
      - "Must map category to exactly one of the allowed explicit list: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
      - "Must mark priority as Urgent if specific severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present."
      - "Must return a 'reason' field of exactly one sentence quoting specific words from the description."
      - "Must output a 'NEEDS_REVIEW' flag for ambiguous entries, otherwise leave blank."

  - name: batch_classify
    role: >
      An orchestrator worker that handles file operations and iterating over a batch of complaints.
    intent: >
      To consume an input CSV file, systematically classify every row via `classify_complaint`, and emit a fully populated output CSV file.
    context: >
      Access to local file system to process input/output CSVs. Deals in data flow and orchestration, delegating all actual semantic classification back to `classify_complaint`.
    enforcement:
      - "Must ignore or strip pre-existing 'category' and 'priority_flag' columns from the input data."
      - "Must apply `classify_complaint` accurately across all rows sequentially (15 rows per city)."
      - "Must write output exclusively to the expected CSV structure (e.g., uc-0a/results_[city].csv)."
