skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as an ordered list of numbered sections and clauses.
    input: >
      path (str) to a UTF-8 plain-text policy file whose clauses start with a number
      in the form N.N (e.g. "2.3 Employees must ...") and whose sections start with
      "N. HEADING".
    output: >
      dict with keys document_title (str), document_reference (str, e.g. HR-POL-001),
      and sections (list of {number: str, heading: str, clauses: list of
      {id: str like "2.3", text: str with line wrapping removed}}), in source order.
    error_handling: >
      File missing or unreadable -> raise a clear error and stop (no summary is better
      than a partial one). No numbered clauses found -> raise an error instead of
      returning an empty structure. Clause text continuing over several lines is
      joined so that no part of a multi-line condition is lost (guards against
      clause omission and condition dropping at load time).

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant, clause-referenced summary that keeps every obligation and condition.
    input: >
      the dict returned by retrieve_policy.
    output: >
      str — plain-text summary with a header naming the source document, one line per
      clause in the form "[2.3] <summary>" grouped under section headings, [VERBATIM]
      markers on clauses quoted in full, and a closing coverage line
      "Clauses in source: N | Clauses in summary: N | All present: YES".
    error_handling: >
      For each clause, the shortened line is checked against the original: every
      number, binding verb (must, will, requires, may, cannot, not, only), absolute
      phrase (regardless, any circumstances, not valid) and named approver must
      survive. If any is lost, the clause is quoted verbatim and flagged [VERBATIM]
      (obligation softening / condition dropping). Clause count mismatch between
      input and summary -> raise an error (clause omission). The finished summary is
      scanned for scope-bleed phrases (standard practice, typically, generally) and
      rejected if any appear.
