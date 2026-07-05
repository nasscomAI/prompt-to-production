# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses it into a list of structured sections, each with a section number, title, and numbered clauses.
    input: A file path string pointing to a .txt policy document with numbered sections and clauses.
    output: A list of dicts, each with keys — section_num (e.g. "2"), title (e.g. "ANNUAL LEAVE"), clauses (list of dicts with clause_num and text).
    error_handling: If the file is not found, raises FileNotFoundError with a clear message. If a section has no recognisable clause numbers, includes the raw section text under clause_num "RAW" so nothing is silently dropped.

  - name: summarize_policy
    description: Takes the structured sections produced by retrieve_policy and writes a clause-complete, obligation-accurate summary to an output text file.
    input: A list of structured section dicts (from retrieve_policy) and an output file path string.
    output: A plain-text file where every clause is summarised with its clause number, binding verbs are preserved, all conditions are stated, and any meaning-loss-risk clause is quoted verbatim with a [VERBATIM] flag.
    error_handling: If a clause text is empty or unparseable, outputs the clause number with the note "[UNABLE TO PARSE — source text missing]" rather than omitting it. Never silently drops a clause.
