skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections, keyed by section number.
    input: file_path (str) — absolute or relative path to a policy .txt file.
    output: A dict mapping section numbers (e.g. "2.3", "5.2") to their full clause text as strings. Also returns document_title and document_reference metadata.
    error_handling: If the file is not found, raise FileNotFoundError with a clear message. If the file is empty, raise ValueError("Policy file is empty — cannot summarise"). If a section number cannot be parsed from the file structure, include the content under key "unparsed" and log a warning.

  - name: summarize_policy
    description: Takes the structured sections returned by retrieve_policy and produces a clause-by-clause compliant summary with every clause cited by number.
    input: sections (dict) — output from retrieve_policy. required_clauses (list of str) — clause numbers that must appear in the output (e.g. ["2.3","2.4","2.5","2.6","2.7","3.2","3.4","5.2","5.3","7.2"]).
    output: A plain-text summary string where each clause is listed with its number, binding verb preserved, and all conditions intact. Multi-condition clauses that risk meaning loss are quoted verbatim with a [QUOTED VERBATIM] tag.
    error_handling: After generating the summary, verify that every clause in required_clauses appears in the output. If any is missing, raise ValueError listing the missing clause numbers. Never return a summary that is missing a required clause.
