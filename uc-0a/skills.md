skills:

- name: classify_complaint
  description: Classifies a single civic complaint row into a standardized category, evaluates priority based on severity keywords, generates a one-sentence justification, and flags ambiguity.
  input:
  type: object
  format: A single row from a CSV data dictionary containing a text description string of the citizen complaint.
  output:
  type: object
  format: A dictionary containing exact category string, priority level, one-sentence reason citing specific description words, and a flag string.
  error_handling: Refuses non-string or missing descriptions; explicitly flags genuinely ambiguous complaints as NEEDS_REVIEW instead of predicting with false confidence; forces strict fallback to the exact allowed taxonomy if taxonomy drift or hallucinated sub-categories are detected.

- name: batch_classify
  description: Iterates through an entire input CSV file of civic complaints, processes each row sequentially using the local classification schema, and exports the unified results to an output CSV file.
  input:
  type: object
  format: File paths for the input CSV file containing unclassified complaint data and the target output CSV file destination.
  output:
  type: string
  format: Path to the generated output CSV file containing structural classifications for all input rows.
  error_handling: Aborts operation if the input file path is missing, unreadable, or structurally corrupted; halts processing or logs malformed rows if critical severity keywords trigger an invalid classification bypass; ensures zero row-by-row structural category variance in the final layout.
