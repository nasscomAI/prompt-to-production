skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from the given path and returns its content as structured numbered sections, preserving all clause identifiers.
    input: Absolute or relative file path to a plain-text policy document (.txt). File must be UTF-8 encoded.
    output: A list of sections, each containing a section heading and a list of clauses. Each clause is a dict with keys 'id' (e.g. "2.3") and 'text' (verbatim clause body).
    error_handling: If the file does not exist or cannot be read, raise FileNotFoundError with the exact path. If the file is empty, raise ValueError("Policy file is empty"). Never silently fall back to partial content.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant, clause-by-clause summary that preserves all binding verbs, all conditions, and all clause references from the source.
    input: The structured section list returned by retrieve_policy (list of dicts with section heading and clauses).
    output: A plain-text summary string, formatted with one line per clause using the pattern "[clause_id] <summary>". Multi-condition obligations list ALL conditions explicitly. Binding verbs (must/will/requires/not permitted) are preserved verbatim.
    error_handling: If a clause cannot be summarised without meaning loss, the skill must flag it with the prefix "FLAG:" and quote the clause verbatim instead of summarising it. Never drop a clause silently.
