skills:

- name: retrieve_policy
  description: 'Loads the .txt HR leave policy file and returns its content parsed into structured, numbered clause sections used as ground truth for summarization.'
  input: 'File path (string) to a UTF-8 plain-text policy file (e.g. ../data/policy-documents/policy_hr_leave.txt) containing numbered clauses such as 2.3, 5.2, 7.2.'
  output: 'Ordered list of clause sections, each an object {clause_id: string (e.g. "5.2"), text: string (verbatim clause text)}, preserving original clause numbering and order with no text paraphrased, dropped, or reordered.'
  error_handling: 'If the file is missing, unreadable, or empty, return an explicit error and fabricate nothing. If no numbered clauses are found, or if any of the 10 expected clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) cannot be located, flag the specific missing clause IDs and halt rather than pass an incomplete structure downstream, guarding against clause omission at the source.'

- name: summarize_policy
  description: 'Takes the structured numbered clause sections and produces a meaning-preserving summary in which every clause is present, tagged with its clause reference, and stripped of no conditions.'
  input: 'Ordered list of clause sections {clause_id, text}, the output of retrieve_policy, covering all 10 numbered clauses.'
  output: 'Text (string) summary in which each of the 10 clauses appears as a distinct entry prefixed by its clause_id, retaining the original binding verb (must / will / requires / may / are forfeited / not permitted) and every condition attached to the obligation.'
  error_handling: 'Refuse to emit a summary that omits any clause, drops any condition of a multi-condition obligation (e.g. clause 5.2 must retain BOTH Department Head AND HR Director approval; clause 5.3 must retain Municipal Commissioner approval), or softens a binding verb. If a clause cannot be summarised without loss of meaning, quote it verbatim and flag it instead of paraphrasing. Never introduce scope-bleed content absent from the source such as "as is standard practice", "typically in government organisations", or "employees are generally expected to"; drop such framing rather than add unsourced information.'
