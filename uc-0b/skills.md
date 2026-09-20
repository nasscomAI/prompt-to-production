# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a UTF-8 policy text file and returns its numbered sections.
    input: A filesystem path to a .txt policy file.
    output: An ordered list of clause references and their complete source wording.
    error_handling: Rejects missing, unreadable, or clause-free files instead of guessing.

  - name: summarize_policy
    description: Produces a clause-referenced summary while preserving all obligations and conditions.
    input: Structured numbered policy sections returned by retrieve_policy.
    output: A UTF-8 Markdown summary containing every source clause.
    error_handling: Preserves ambiguous clauses verbatim and flags them for review; never invents a resolution.
