# skills:

# &#x20; - name: retrieve\_policy

# &#x20;   description: Loads a .txt policy file and returns its content as structured numbered sections, handling clauses that wrap across multiple lines.

# &#x20;   input: File path to a policy .txt document.

# &#x20;   output: A list of dicts, each with a clause number and its full text.

# &#x20;   error\_handling: If the file cannot be opened or contains no recognizable numbered clauses, raise a clear error rather than silently returning an empty summary.

# 

# &#x20; - name: summarize\_policy

# &#x20;   description: Takes structured clause sections and produces a compliant summary referencing every clause number, preserving all conditions for high-risk multi-condition clauses.

# &#x20;   input: A list of clause dicts (number, text) from retrieve\_policy.

# &#x20;   output: A formatted summary string with one line per clause, clause number included.

# &#x20;   error\_handling: If a clause is flagged high-risk for condition loss, output it verbatim rather than attempt compression.

