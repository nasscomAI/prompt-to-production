skills:
  - name: retrieve_policy
    description: Loads a policy document text file and returns its numbered clauses as structured sections.
    input:
      type: object
      format: "{ input_path: string }"
    output:
      type: object
      format: "{ sections: Array<{ clause: string, text: string }> }"
    error_handling: >
      If the input file is missing or unreadable, raise an error; if numbered clauses cannot be reliably extracted, return an empty sections list and include a clear failure indication.

  - name: summarize_policy
    description: Takes structured policy sections and generates a compliant summary preserving each required clause and its obligations.
    input:
      type: object
      format: "{ sections: Array<{ clause: string, text: string }> }"
    output:
      type: object
      format: "{ summary: string }"
    error_handling: >
      If required clauses are missing or ambiguous, include verbatim quotes for those clauses and add a flag indicating review is needed; never fabricate missing content.
