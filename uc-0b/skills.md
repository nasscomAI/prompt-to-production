skills:
  - name: retrieve_policy
    description: Loads a plain-text policy and separates it into ordered, numbered clauses with their section headings.
    input: "Path to a UTF-8 .txt policy file."
    output: "An ordered PolicyDocument containing document metadata, section headings, clause references and complete clause text."
    error_handling: "Stop with a clear error if the file is unreadable, is not a .txt file, contains no numbered clauses, has text that cannot be assigned safely to a clause or repeats a clause reference. Never infer missing clause text."

  - name: summarize_policy
    description: Produces a faithful clause-by-clause extractive summary while preserving every obligation and condition.
    input: "An ordered PolicyDocument returned by retrieve_policy."
    output: "Plain text containing every clause reference exactly once, grouped under its source section heading."
    error_handling: "Quote a clause verbatim and flag it as VERBATIM — meaning-sensitive whenever shortening could change meaning; reject output if any source clause is missing, duplicated or altered."
