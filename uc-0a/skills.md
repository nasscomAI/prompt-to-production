- name: classify_complaint
  description: Reads a single complaint row and classifies it into a category, priority, and reason, applying a flag if ambiguous.
  input: 
    type: dict
    format: row dictionary from CSV containing complaint description
  output:
    type: dict
    format: row dictionary with keys complaint_id, category, priority, reason, flag
  error_handling: Return category="Other" and flag="NEEDS_REVIEW" if the description is genuinely ambiguous or unrecognizable. If no reason can be cited, still provide the row with a generic reason and NEEDS_REVIEW.

- name: batch_classify
  description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the output to a CSV.
  input:
    type: string
    format: path to input CSV file
  output:
    type: string
    format: path to output CSV file
  error_handling: If a row fails to process, skip or flag it, but do not crash the batch job. Continue processing the remaining rows.
