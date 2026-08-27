- name: retrieve_documents
  description: Loads HR, IT, and Finance policy files and indexes them into a searchable structure mapped by document name and section number.
  input: List of Strings representing absolute paths to the three mandatory policy files.
  output: Dictionary/Object containing indexed policy sections keyed by document and section number.
  error_handling: Aborts with a fatal error if any of the three policy documents are missing or unreadable; ensures all sections are correctly parsed before indexing.

- name: answer_question
  description: Searches the indexed policy repository to provide a granular, single-source answer or the exact mandated refusal template.
  input: Object containing the 'user_question' String and the indexed 'policy_collection'.
  output: String containing a cited answer (Doc + Section) or the verbatim refusal template.
  error_handling: Prevents 'Cross-document blending' by refusing to produce a combined answer; eliminates 'Hedged hallucination' by forcing a switch to the refusal template if a definitive match is not found; ensures 'Condition dropping' is avoided by quoting complex multi-condition clauses verbatim.
