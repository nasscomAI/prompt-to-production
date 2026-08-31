# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: >
      One complaint row as a dict containing at least the complaint description
      and complaint_id (e.g. a row from the input CSV).
    output: >
      A dict with exactly the keys: category, priority, reason, flag.
      - category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road
        Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
      - priority: one of Urgent, Standard, Low.
      - reason: a one-sentence justification citing specific words from the
        description.
      - flag: NEEDS_REVIEW or blank.
    error_handling: >
      Use only the exact allowed categories and priority values defined in
      agents.md — never invent or rename them. Apply the mandatory severity
      keyword rule: if the description contains injury, child, school,
      hospital, ambulance, fire, hazard, fell, or collapse, priority must be
      Urgent. Generate a one-sentence reason grounded in the complaint
      description. Set flag to NEEDS_REVIEW only when the category is genuinely
      ambiguous; otherwise leave it blank. Never modify the input data. If the
      complaint_id or description is missing, do not fabricate them.

  - name: batch_classify
    description: Reads a complaint CSV, applies classify_complaint to every row, and writes the results CSV.
    input: >
      An input CSV path and an output CSV path. The input CSV contains complaint
      rows, each with at least a description and a complaint_id.
    output: >
      A CSV written to the output path with one output row per complaint and
      columns exactly: complaint_id, category, priority, reason, flag. The
      complaint_id is preserved from the input.
    error_handling: >
      Read all complaint rows from the input CSV and apply classify_complaint
      to each. Handle malformed or null rows without crashing the entire batch —
      produce output even if some rows fail. Ensure every output row has the
      required fields; for a failed/ambiguous row, still emit the five columns.
      Do not modify the input CSV.
