skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag using the enforced UC-0A schema.
    input: One complaint row as a dictionary/object with at least description text; optional row metadata fields may be present but no external context is used.
    output: One dictionary/object with category (exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent, Standard, or Low), reason (exactly one sentence citing concrete words from description), and flag (NEEDS_REVIEW or blank).
    error_handling: If description is missing, empty, or non-text, return category as Other, priority as Standard, reason as one sentence stating missing usable description evidence, and flag as NEEDS_REVIEW; if category evidence is genuinely ambiguous, return category as Other with flag NEEDS_REVIEW; if severity keywords appear (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse), force priority to Urgent.

  - name: batch_classify
    description: Reads a city CSV input file, applies classify_complaint to each row, and writes a deterministic results CSV.
    input: CSV path matching ../data/city-test-files/test_[city].csv with complaint rows where category and priority labels are absent.
    output: CSV written to uc-0a/results_[city].csv containing original rows plus classification columns category, priority, reason, and flag with exact allowed values and formats.
    error_handling: If input file is missing, unreadable, or malformed CSV, stop and return a clear processing error without partial silent success; for row-level invalid or ambiguous descriptions, continue processing remaining rows while writing that row as category Other, priority Standard unless severity keywords force Urgent, reason as one sentence with available evidence, and flag as NEEDS_REVIEW.
