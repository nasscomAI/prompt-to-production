- name: retrieve_policy
  description: >
    Loads HR leave policy text file and extracts structured numbered clauses.

  input:
    type: text file
    format: policy document

  output:
    type: structured sections
    format: numbered policy clauses

  error_handling: >
    Preserve clause numbering and avoid skipping malformed sections.

- name: summarize_policy
  description: >
    Produces compliant policy summaries while preserving obligations,
    conditions, approvals, penalties, and timelines.

  input:
    type: structured policy sections
    format: numbered clauses

  output:
    type: text summary
    format: clause-referenced summary

  error_handling: >
    If a clause cannot be summarized safely without meaning loss,
    quote it directly and flag it clearly.