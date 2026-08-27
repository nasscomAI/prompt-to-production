# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content clearly formatted as structured numbered sections preserving all original clauses.
    input: The absolute or relative path to a plain text (.txt) policy file.
    output: A list or structured text dictionary of explicitly separated, explicitly numbered sections exactly mapping the source's paragraphs.
    error_handling: Refuses to parse or raises error if the file format isn't recognized, or if it lacks numbered sections.

  - name: summarize_policy
    description: Takes the structured sections, reads every single clause, and produces a highly compliant, condensed summary while keeping the references, constraints, and conditions identical to the source.
    input: The structured sections returned by the retrieve_policy skill.
    output: A compliant textual summary citing every clause explicitly. Multi-condition requirements must remain intact. Any clause that cannot be cleanly summarized must be flagged and quoted exactly.
    error_handling: If standard AI tools struggle to summarize without changing meaning, it gracefully backs off to exact-quoting that line rather than risking meaning shift.
