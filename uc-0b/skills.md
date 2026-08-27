- name: retrieve_policy
  description: Loads the HR leave policy .txt file and returns its content as structured numbered sections for downstream processing.
  input: .txt file path (string)
  output: Structured dictionary mapping clause numbers to their full text content.
  error_handling: Raises an error if file is missing or cannot be read; if a clause number is missing from the expected inventory, it flags the gap before continuing.

- name: summarize_policy
  description: Produces a compliant policy summary from structured sections, preserving all clause references, binding verbs, and multi-condition requirements.
  input: Structured dictionary of clause sections, ground truth clause inventory
  output: Summary text with clause references and verbatim quotes where meaning would be lost.
  error_handling: If any of the 10 required clauses are missing from the summary, it raises an error; if a clause cannot be summarised without meaning loss, it quotes the clause verbatim and flags it.
