# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: path (string) to a UTF-8 .txt policy document with numbered sections (e.g. "2. ANNUAL LEAVE") and clauses (e.g. "2.3 ...").
    output: Dict with header lines and a list of sections; each section has section number, title, and a list of clauses (id + full text, continuation lines joined).
    error_handling: Missing file or non-UTF-8 encoding exits with a clear stderr message and exit code 1; documents without any numbered sections are rejected rather than guessed at.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary in which every clause appears with all conditions preserved.
    input: Structured policy dict as produced by retrieve_policy.
    output: Summary text organised by section — every clause id present, multi-condition clauses quoted verbatim and flagged [VERBATIM]; also returns the list of required clauses missing from the source (empty list when complete).
    error_handling: Clauses that cannot be condensed without meaning loss are quoted verbatim and flagged instead of paraphrased; if any of the 10 ground-truth clauses are missing, the run reports them on stderr and exits with code 2 so the failure is visible.
