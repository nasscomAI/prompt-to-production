# UC-0A Complaint Classifier Skills

role: >
  Classify citizen-complaint descriptions into the project taxonomy and produce
  a complete, auditable result. The skills do not invent incident details,
  sub-categories, or confidence beyond the supplied complaint text.

intent: >
  Each valid complaint produces exactly one category, one priority, a
  one-sentence reason grounded in the description, and a review flag only
  when the category cannot genuinely be determined from that description.

context: >
  Use only the complaint description and the classification schema in
  README.md. Do not use external knowledge, unstated location facts, prior
  rows, or inferred details to select a category or priority.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "priority must be exactly one of: Urgent, Standard, Low; use Urgent when the description contains injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse (case-insensitive)."
  - "reason must be one sentence and cite specific words from the complaint description."
  - "For a genuinely ambiguous category, set category to Other and flag to NEEDS_REVIEW; otherwise flag must be blank."

skills:
  - name: classify_complaint
    description: >
      Classifies one citizen-complaint row into the required category,
      priority, reason, and review flag.
    input: >
      One row or object containing a non-empty description string.
    output: >
      An object with category, priority, reason, and flag fields that satisfies
      every enforcement rule above.
    error_handling: >
      Reject a missing, non-string, or blank description with a validation
      error. When a valid description does not establish a category, return
      category: Other and flag: NEEDS_REVIEW rather than guessing.

  - name: batch_classify
    description: >
      Reads a complaint CSV, applies classify_complaint to every row, and
      writes a result CSV.
    input: >
      An input CSV whose rows contain a non-empty description column, plus an
      output CSV path.
    output: >
      A CSV preserving the input rows and adding category, priority, reason,
      and flag columns for every successfully classified row.
    error_handling: >
      Validate the input file and description column before writing output; on
      an unreadable CSV or an invalid row, report the row and validation error
      instead of silently emitting an ungrounded classification.
