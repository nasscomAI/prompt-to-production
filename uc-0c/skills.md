skills:

- name: load_dataset
  description: >Reads the target CSV budget file, validates structural columns, and tracks missing entries before serving records to calculation layers.
  input:type: "string"format: >Local filesystem path to the ward_budget.csv document.output:type: "object"format: >A structured dictionary holding an itemized dataset array alongside an automated summary of isolated null rows.
  error_handling: >Aborts program execution if the source file is missing, empty, or unreadable; flags total raw null occurrences explicitly instead of executing silent drop sequences.

- name: compute_growth
  description: >Evaluates localized growth indexes across filtered temporal arrays while mapping mandatory algorithmic execution formula labels.
  input:type: "object"format: >Configuration matrix parameters detailing specific target ward, category, and selected metric growth-type string.
  output:type: "string"format: >A structured tabular report displaying row-by-row growth computations coupled with explicit tracking formulas and null explanations.
  error_handling: >Refuses execution automatically with a termination prompt if the growth-type configuration string is omitted or if multi-ward global aggregation queries are submitted; routes individual missing data nodes to output strings flagged with the verbatim context from their corresponding source notes section.
