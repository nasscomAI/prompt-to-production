# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and returns its content parsed into structured numbered sections.
    input: Path to a UTF-8 plain-text (.txt) policy file whose clauses follow the pattern "N.M <text>" grouped under section headers.
    output: An ordered list of sections; each section has its heading plus a list of clauses keyed by their full clause number ("2.3") with the complete clause text, including continuation lines.
    error_handling: A missing or unreadable file exits with a clear error before anything is processed; a file yielding zero recognised clauses aborts with a parse error rather than returning empty structure; clause numbers are kept as literal strings so "2.10" is never confused with "2.1".

  - name: summarize_policy
    description: Produces a meaning-preserving summary of structured policy sections in which every clause survives with identical obligations and binding force.
    input: The ordered list of sections returned by retrieve_policy.
    output: Plain-text summary in which every clause appears under its own clause number with all conditions intact and binding verbs preserved; clauses that cannot be safely condensed are quoted verbatim and marked [FLAGGED: quoted verbatim].
    error_handling: A clause whose condensation would drop any condition, quantity, approver, or binding verb is quoted verbatim and flagged instead of paraphrased; an input missing expected clause numbering aborts with an error rather than producing a partial summary; never invents content to fill gaps in the input.
