# skills.md
skills:
  - name: retrieve_policy
    description: Loads the policy .txt file and parses it into structured numbered clauses.
    input: file_path (str) - path to a .txt policy document.
    output: A list of dicts, each with keys "clause" (e.g. "2.3") and "text" (the full clause text, including all conditions).
    error_handling: If the file is missing or unreadable, raises a clear error rather than returning an empty/silent result.

  - name: summarize_policy
    description: Takes structured clauses and produces a summary that preserves every clause and every condition within it.
    input: A list of clause dicts from retrieve_policy.
    output: A formatted text string, one line/block per clause, with high-risk multi-condition clauses marked [VERBATIM] and preserved word-for-word.
    error_handling: If a clause's text is empty, it is still listed with a note "[EMPTY CLAUSE — SOURCE ERROR]" rather than silently skipped.
