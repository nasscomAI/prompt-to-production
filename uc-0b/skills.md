# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns it as structured numbered sections and clauses.
    input: path to a policy .txt file
    output: dict — {sections: [{number, title}], clauses: [{number, section, text}], version: str}
    error_handling: Missing or empty file → raises a clear error; non-clause lines (headers, separators, metadata) are skipped, never misread as clauses.

  - name: summarize_policy
    description: Takes structured sections and produces a lossless summary with clause references for every clause.
    input: dict from retrieve_policy
    output: str — summary text where every clause is present with its number and all conditions preserved
    error_handling: Clauses not safely summarisable without meaning loss are retained near-verbatim; a verification pass fails loudly if a clause or condition is missing.
