# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads the policy .txt file and parses its contents into structured, numbered clauses to guarantee no text is missed.
    input: File path to the raw policy document (.txt format).
    output: A structured dictionary or list where each item is a distinct numbered clause from the text.
    error_handling: Raise a FileNotFoundError if the file is missing; if the text lacks numbered clauses, fail and prompt for manual review to prevent silent omissions.

  - name: summarize_policy
    description: Takes structured clauses and generates a strict, legally-compliant summary while preserving all multi-condition obligations and quoting ambiguous text.
    input: Structured clause data returned by retrieve_policy.
    output: A formatted text summary explicitly referencing each clause and quoting exact language where meaning loss is a risk.
    error_handling: If a clause cannot be summarized without potentially dropping a condition or softening its meaning, output the exact verbatim text of the clause and flag it with [VERBATIM_REQUIRED].
