skills:
  - name: retrieve_policy
    description: Loads a text policy file and returns its content as ordered numbered sections.
    input: "UTF-8 .txt file path containing numbered policy clauses."
    output: "Ordered list of dictionaries with section number and full clause text."
    error_handling: "Raises clear errors for missing files, unreadable text, absent numbered clauses, null content, or ambiguous section parsing."
  - name: summarize_policy
    description: Produces a clause-preserving summary with clause references and all binding conditions intact.
    input: "Ordered numbered sections from retrieve_policy."
    output: "Plain-text summary containing every clause number and compliant summarized or quoted clause text."
    error_handling: "Raises clear errors for missing critical clauses, dropped approvers, unsupported wording, blank summaries, or any clause that cannot be safely represented."
