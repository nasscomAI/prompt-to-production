- name: retrieve_policy
  description: Loads a .txt policy file and returns the content as structured numbered sections.
  input:
    type: string
    format: path to the policy text file
  output:
    type: list of dicts
    format: structured list where each dict contains a 'clause_number' and 'text'
  error_handling: If the file is unreadable or malformed, return an error indicating the specific failure mode.

- name: summarize_policy
  description: Takes structured sections and produces a compliant summary with clause references, ensuring no multi-condition obligations drop conditions and no clause is omitted.
  input:
    type: list of dicts
    format: structured list from retrieve_policy
  output:
    type: string
    format: compliant summary text preserving all binding obligations
  error_handling: If a clause cannot be summarized without loss of meaning, quote it verbatim and flag it in the summary output.
