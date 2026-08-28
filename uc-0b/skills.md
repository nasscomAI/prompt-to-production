skills:

- name: retrieve_policy
  description: Loads the raw policy text file and parses its contents into structurally indexed, numbered sections matching the original document constraints.
  input:type: "string"format: >Local filesystem path pointing to the target .txt policy source document.
  output:type: "object"format: >A structured dictionary map associating specific clause numbers to their respective raw string text obligations.
  error_handling: Aborts processing if the file path is unreadable, empty, or missing; rejects parsing lines that fail to isolate numbered subsections; triggers validation failures if target section boundaries cannot be structurally extracted.
- name: summarize_policy
  description: Processes structured sections to generate an exact policy summary while preserving all condition sets and cross-referencing mandatory clause tokens.
  input:type: "object"format: >A structured dictionary map consisting of indexed clause keys and their associated ground truth obligation strings.
  output:type: "string"format: >A complete, compiled summary block mapping every single clause with intact conditional qualifiers and explicit clause indicators.
  error_handling: Flags a clause configuration and quotes it verbatim if any truncation risks obligation softening; falls back to an error block if any of the 10 core ground-truth clauses are dropped; strips external context phrases to eliminate scope bleed.
