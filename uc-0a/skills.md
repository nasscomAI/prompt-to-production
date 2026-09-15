skills:
  - name: classify_complaint
    description: >
      Classifies a single municipal complaint into an allowed category, determines its priority based on severity triggers, provides a justification citing description keywords, and flags ambiguous complaints.
    input: >
      A dictionary representing a single complaint row with keys including complaint_id, description, and optional metadata fields (date_raised, city, ward, location, reported_by, days_open).
    output: >
      A dictionary containing complaint_id (string), category (string from allowed taxonomy: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (string: Urgent, Standard, Low), reason (single sentence citing specific words from description), and flag ('NEEDS_REVIEW' or empty string '').
    error_handling: >
      If the description is missing, empty, or genuinely ambiguous, set category to 'Other', priority to 'Standard' (or 'Urgent' if severity keywords exist), reason explaining the ambiguity citing available text, and flag to 'NEEDS_REVIEW'. If an invalid or unmapped category is encountered, fallback to 'Other' with flag 'NEEDS_REVIEW' to prevent taxonomy drift and hallucinated sub-categories. If any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) is present, priority must always escalate to 'Urgent' to avoid severity blindness.

  - name: batch_classify
    description: >
      Reads an input CSV file of municipal complaints, applies classify_complaint to each record, and writes the structured classification results to a target output CSV file.
    input: >
      Two file paths as strings: input_path (path to input CSV file containing complaint rows with at least complaint_id and description) and output_path (path where the classified CSV file will be written).
    output: >
      A CSV file written to output_path containing columns complaint_id, category, priority, reason, and flag, returning None or a completion summary dictionary.
    error_handling: >
      Handles missing input files by raising FileNotFoundError; skips or flags corrupted/malformed CSV rows with flag 'NEEDS_REVIEW' without crashing the batch pipeline; ensures partial or bad rows still produce an output record so no complaints are silently dropped.
