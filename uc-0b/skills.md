# skills.md

skills:

- name: retrieve_policy
  description: Load a policy text file and return the document as structured numbered sections for clause-aware summarization.
  input: A file path to a .txt policy document.
  output: A structured representation of the policy with numbered sections and clause text.
  error_handling: If the file is missing or unreadable, return an error message and do not guess at the policy content.

- name: summarize_policy
  description: Summarize a structured policy into a clause-preserving output that includes all required references and preserves conditions.
  input: A structured policy object containing numbered clauses and text.
  output: A summary string with clause references, preserving all mandatory conditions and quoting any clause that cannot be safely shortened.
  error_handling: If a clause is ambiguous or meaning would be lost in paraphrase, quote the original clause verbatim and annotate it for review.
