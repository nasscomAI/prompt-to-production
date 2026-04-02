- name: "retrieve_policy"
  description: "Loads a .txt policy file and returns the content as structured numbered sections."
  input:
    type: "string (file path)"
    format: "File path ending in .txt"
  output:
    type: "list/array"
    format: "Structured numbered sections"
  error_handling: "Fail if file is not found or unreadable. Return parse error if document lacks expected structuring."

- name: "summarize_policy"
  description: "Takes structured sections and produces a compliant summary with clause references."
  input:
    type: "list/array"
    format: "Structured numbered sections"
  output:
    type: "string"
    format: "Compliant summary with clause references"
  error_handling: "If a clause cannot be confidently summarized without meaning loss or scope bleed, quote it verbatim and flag it in the output instead of summarizing."
