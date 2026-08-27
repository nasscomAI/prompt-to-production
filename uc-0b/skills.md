skills:
  - name: retrieve_policy
    description: Parses a policy .txt file into an ordered structure of sections and numbered clauses, joining wrapped/indented lines back into a single clause string so no sentence is split or lost.
    input: Path to a policy .txt file.
    output: A dict with document metadata (doc_ref, version, effective) and a list of sections, each holding clause objects ({id, text}) in document order.
    error_handling: Raises FileNotFoundError with the attempted path if the file does not exist; raises ValueError if no numbered clauses (pattern "N.N") are found, since that indicates an unparsable or empty document.

  - name: summarize_policy
    description: Converts parsed sections/clauses into a compliance-safe summary that preserves every clause and every condition within multi-part obligations, flags dense multi-condition clauses, and appends a self-check against the known ground-truth clause list from agents.md.
    input: The dict returned by retrieve_policy.
    output: A formatted string containing the section-by-section clause summary plus a COMPLIANCE CHECK footer listing each ground-truth clause as present/MISSING.
    error_handling: If a ground-truth clause is missing from the parsed document, it is listed as MISSING in the compliance footer rather than silently dropped, so the gap stays visible instead of hidden.
