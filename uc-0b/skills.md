skills:
  - name: retrieve_policy
    description: Load a plaintext policy file and parse it into structured numbered sections and clauses.
    input: file path (string) pointing to .txt policy document
    output: object with fields {sections: list of {section_num: string, clauses: list of {clause_num: string, text: string, binding_verb: string}}}
    error_handling: If file does not exist, raise IOError. If file is not valid UTF-8 text, raise encoding error. If file cannot be parsed into numbered sections, raise parsing error with indication of where structure breaks down. Never skip clauses during parsing.
  
  - name: summarize_policy
    description: Transform structured policy sections into a compliant summary that preserves all clauses and multi-condition obligations.
    input: object from retrieve_policy containing sections and clauses
    output: string (summary text) with all 10 clauses preserved, each with clause reference and reason field
    error_handling: If any of the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing from input, raise error listing which clauses are missing. If a clause contains multiple conditions (e.g., 5.2 with two approvers), preserve ALL conditions in summary or quote verbatim and flag NEEDS_REVIEW. If summary would introduce scope bleed or unsourced information, reject and raise error. If clause cannot be summarized without meaning loss, output clause verbatim in summary with [QUOTED] marker.
