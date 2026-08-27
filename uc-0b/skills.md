skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from disk and returns its content as structured
      numbered sections, preserving all clause numbers and original wording.
    input: >
      File path (string) pointing to a plain-text policy document. Expected format:
      sections delimited by headings and numbered clauses (e.g. "2.3 Employees must ...").
    output: >
      A list of sections, each containing the section heading and an ordered list of
      clause objects with fields: clause_id (string, e.g. "2.3"), text (string, verbatim).
    error_handling: >
      If the file path does not exist or is unreadable, return an error object with
      reason "file_not_found" or "read_error" and halt — do not proceed to summarisation.
      If the file contains no recognisable numbered clauses, return error reason
      "no_clauses_detected" and halt.

  - name: summarize_policy
    description: >
      Takes the structured sections produced by retrieve_policy and produces a compliant
      summary in which every clause is present, all multi-condition obligations are intact,
      and no language outside the source document is introduced.
    input: >
      List of section objects (output of retrieve_policy): each section has a heading and
      an ordered list of clause objects with clause_id and verbatim text fields.
    output: >
      A plain-text summary organised by section. Each clause is rendered as:
      "Clause <id>: <summary or verbatim quote>". Clauses that cannot be summarised
      without meaning loss are quoted verbatim and marked "[verbatim — meaning-loss risk]".
    error_handling: >
      If any of the 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3,
      7.2) are absent from the input, return an error listing the missing clause IDs and
      halt rather than producing an incomplete summary. Do not infer or reconstruct
      missing clauses from general knowledge.
