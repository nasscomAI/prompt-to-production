skills:

&#x20; - name: retrieve\_policy

&#x20;   description: Loads a .txt policy file and returns its content as structured numbered sections.

&#x20;   input: file\_path (path to a .txt policy document).

&#x20;   output: A structured representation (e.g. list of dicts) with clause number, section title, and clause text for each numbered clause found.

&#x20;   error\_handling: If the file is missing or empty, raise a clear error rather than returning partial/empty data silently.



&#x20; - name: summarize\_policy

&#x20;   description: Takes structured policy sections and produces a compliant summary that preserves every clause, condition, and binding obligation.

&#x20;   input: The structured sections returned by retrieve\_policy.

&#x20;   output: A plain text summary, referencing each clause by number, with all conditions and binding language preserved.

&#x20;   error\_handling: If a clause cannot be summarized without losing meaning, include it verbatim in the output rather than omitting or guessing.

